import { Component, Inject, OnDestroy, OnInit, ViewEncapsulation } from "@angular/core";
import { ActiveWindowWidgetProps } from "../../../../bindings/widget/active_window/ActiveWindowWidgetProps";
import { Event as TauriEvent, UnlistenFn, listen, emit } from "@tauri-apps/api/event";
import { currentMonitor, WebviewWindow } from "@tauri-apps/api/window";
import { invoke } from "@tauri-apps/api/tauri";
import { tryFormatEval } from "../../../../utils/format";
import { ActiveWindowPayload } from "../../../../bindings/widget/active_window/ActiveWindowPayload";
import { WIDGET_PROPS } from "..";
import { CallbackWidgetComponent } from "../callback-widget.component";
import { ActiveWindowCallbackType } from "../../../../bindings/widget/active_window/ActiveWindowCallbackType";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import {
    JSON_VIEWER_DEFAULT_HEIGHT,
    JSON_VIEWER_DEFAULT_PADDING,
    JSON_VIEWER_DEFAULT_WIDTH,
} from "../../popups/json-viewer/json-viewer.component";
import { PopupOptions, PopupService } from "../../../services/popup.service";

const NAVIGATION_CLASSES = [
    "SHELLDLL_DefView",
    "Windows.UI.Input.InputSite.WindowClass",
    "ToolbarWindow32",
    "SysTreeView32",
    "DirectUIHWND",
    "ComboLBox",
];
const IGNORED_PROCESSES = ["SearchHost.exe", "ShellExperienceHost.exe"];
const IGNORED_CLASSES = [
    "WorkerW",
    "NotifyIconOverflowWindow",
    "XamlExplorerHostIslandWindow",
    "Windows.UI.Core.CoreWindow",
];
const DEFAULT_LABEL = "${win.title} ${win.class} ${win.process}";

@Component({
    selector: "active-window-widget",
    templateUrl: "./active-window-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class ActiveWindowWidgetComponent extends CallbackWidgetComponent implements OnInit, OnDestroy {
    public activeLabelTooltip?: string;
    public activeLabelFormatted?: string;
    public isHidden = true;
    public isError = false;

    private ignoredClasses: string[];
    private ignoredProcesses: string[];
    private ignoredTitles: string[];
    private unformattedActiveLabel: string;
    private currentMonitorName: string | null | undefined;
    private showAltLabel = false;
    private activeWindow?: ActiveWindowPayload;
    private activeWindowUnlistener?: UnlistenFn;
    private webview: WebviewWindow;
    private popupOptions: PopupOptions;

    public constructor(
        private popupService: PopupService,
        @Inject(WIDGET_PROPS) public props?: ActiveWindowWidgetProps
    ) {
        super(props?.callbacks as WidgetCallbacks<ActiveWindowCallbackType>);
        this.unformattedActiveLabel = this.props?.label ?? DEFAULT_LABEL;
        this.ignoredTitles = [...(this.props?.ignored_windows?.by_class ?? [])];
        this.ignoredClasses = [...IGNORED_CLASSES, ...(this.props?.ignored_windows?.by_title ?? [])];
        this.ignoredProcesses = [...IGNORED_PROCESSES, ...(this.props?.ignored_windows?.by_process ?? [])];
        this.popupOptions = {
            width: this.props?.json_viewer?.width ?? JSON_VIEWER_DEFAULT_WIDTH,
            height: this.props?.json_viewer?.height ?? JSON_VIEWER_DEFAULT_HEIGHT,
            padding: this.props?.json_viewer?.padding ?? JSON_VIEWER_DEFAULT_PADDING,
        };
    }

    public async ngOnInit(): Promise<void> {
        this.currentMonitorName = (await currentMonitor())?.name;
        this.activeWindowUnlistener = await listen("ActiveWindowChanged", this.onActiveWindowChange.bind(this));
        await invoke("win32_init_event_hook");
        await invoke("detect_foreground_window");
        this.isHidden = false;
        this.activeLabelFormatted = this.unformattedActiveLabel;
        this.updateLabels();
    }

    public async ngOnDestroy(): Promise<void> {
        if (this.activeWindowUnlistener) {
            this.activeWindowUnlistener();
        }
    }

    protected mapCallback(callbackType: string): ((event: MouseEvent, callbackType: string) => void) | undefined {
        switch (callbackType) {
            case "toggle_label":
                return this.toggleActiveLabel.bind(this);
            case "json_viewer":
                return this.toggleJsonViewer.bind(this);
            default:
                return;
        }
    }

    private async toggleJsonViewer(event: MouseEvent): Promise<void> {
        if (!this.webview && this.isCallbackTypePresent("json_viewer")) {
            this.webview = await this.popupService.create(event, "json_viewer", this.popupOptions);
            const initUnlisten = await listen(`${this.webview?.label}_ngOnInit`, async () => {
                await emit(`${this.webview?.label}_data`, this.activeWindow);
                initUnlisten();
            });
        } else {
            this.popupService.toggleVisiblity(this.webview, event, this.popupOptions);
        }
    }

    public getClasses(): any {
        const classes: any = { error: this.isError, hidden: this.isHidden };

        if (this.props?.class) {
            classes[this.props?.class] = true;
        }

        return classes;
    }

    private async onActiveWindowChange(event: TauriEvent<ActiveWindowPayload>): Promise<void> {
        if (
            event.payload.title &&
            this.activeWindow?.title != event.payload.title &&
            event.payload.title !== "yasb-popup" &&
            !(
                event.payload.exe_name === "msedgewebview2.exe" &&
                ["about:blank", "Untitled"].includes(event.payload.title)
            )
        ) {
            this.activeWindow = event.payload;
            this.execData = this.activeWindow;
            if ((await this.webview?.isVisible()) && (this.props?.json_viewer?.update_on_change ?? true)) {
                await emit(`${this.webview?.label}_data`, this.activeWindow);
            }
            this.hideOrUpdateContent();
        }
    }

    private async hideOrUpdateContent(): Promise<void> {
        if (
            this.ignoredProcesses?.includes(this.activeWindow?.exe_name ?? "") ||
            this.ignoredClasses?.includes(this.activeWindow?.class ?? "") ||
            this.ignoredTitles?.includes(this.activeWindow?.title ?? "")
        ) {
            this.isHidden = true;
        } else {
            this.isHidden = !!this.props?.is_monitor_exclusive && this.activeWindow?.monitor != this.currentMonitorName;

            if (!this.isHidden && NAVIGATION_CLASSES.includes(this.activeWindow?.class ?? "")) {
                return await invoke("detect_foreground_window");
            }

            this.updateLabels();
        }
    }

    private updateLabels(): void {
        if (!this.activeWindow) {
            this.isHidden = true;
            return;
        }

        try {
            this.activeLabelFormatted = tryFormatEval(this.unformattedActiveLabel, this.activeWindow);
            this.isError = false;
        } catch (error) {
            this.activeLabelFormatted = this.unformattedActiveLabel;
            this.activeLabelTooltip = `Error formatting active label:\n\n${(error as Error).message}`;
            this.isError = true;
        }

        if (
            this.props?.label_max_len &&
            this.activeLabelFormatted &&
            this.activeLabelFormatted.length > this.props.label_max_len
        ) {
            this.activeLabelFormatted = this.activeLabelFormatted.substring(0, this.props.label_max_len) + "...";
        }
    }

    public async toggleActiveLabel(): Promise<void> {
        this.showAltLabel = !this.showAltLabel;
        this.unformattedActiveLabel = (this.showAltLabel ? this.props?.label_alt : this.props?.label) ?? DEFAULT_LABEL;
        this.updateLabels();
    }
}
