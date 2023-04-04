import { Component, Inject, OnInit, ViewEncapsulation } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { emit, listen } from "@tauri-apps/api/event";
import { WebviewWindow } from "@tauri-apps/api/window";
import { WIDGET_PROPS } from "..";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import { SysInfoCallbackType } from "../../../../bindings/widget/sysinfo/SysInfoCallbackType";
import { SysInfoWidgetProps } from "../../../../bindings/widget/sysinfo/SysInfoWidgetProps";
import { SystemInformationPayload } from "../../../../bindings/widget/sysinfo/SystemInformationPayload";
import { tryFormatEval } from "../../../../utils/eval";
import { PopupOptions, PopupService } from "../../../services/popup.service";
import {
    JSON_VIEWER_DEFAULT_HEIGHT,
    JSON_VIEWER_DEFAULT_PADDING,
    JSON_VIEWER_DEFAULT_WIDTH,
} from "../../popups/json-viewer/json-viewer.component";
import { CallbackWidgetComponent } from "../callback-widget.component";

const DEFAULT_LABEL = "hostname: ${data.sys.host}";

@Component({
    selector: "sys-info-widget",
    templateUrl: "./sys-info-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class SysInfoWidgetComponent extends CallbackWidgetComponent implements OnInit {
    public isHidden = true;
    public isError = false;
    public activeLabelFormatted?: string;
    public errorTooltip?: string;

    private label: string;
    private labelAlt?: string;
    private sysInfo?: SystemInformationPayload;
    private showAltLabel = false;
    private activeLabel: string;
    private webview: WebviewWindow;
    private popupOptions: PopupOptions;

    constructor(private popupService: PopupService, @Inject(WIDGET_PROPS) public props?: SysInfoWidgetProps) {
        super(props?.callbacks as WidgetCallbacks<SysInfoCallbackType>);
        this.label = this.props?.label ?? DEFAULT_LABEL;
        this.labelAlt = this.props?.label_alt ?? undefined;
        this.activeLabel = this.label;
        this.popupOptions = {
            width: this.props?.json_viewer?.width ?? JSON_VIEWER_DEFAULT_WIDTH,
            height: this.props?.json_viewer?.height ?? JSON_VIEWER_DEFAULT_HEIGHT,
            padding: this.props?.json_viewer?.padding ?? JSON_VIEWER_DEFAULT_PADDING,
        };
    }

    public async ngOnInit(): Promise<void> {
        await this.queryInfo();
        this.props?.interval && setInterval(this.queryInfo.bind(this), this.props.interval);
    }

    private async toggleJsonViewer(event: MouseEvent): Promise<void> {
        if (!this.webview && this.isCallbackTypePresent("json_viewer")) {
            this.webview = await this.popupService.create(event, "json_viewer", this.popupOptions);
            const initUnlisten = await listen(`${this.webview?.label}_ngOnInit`, async () => {
                await emit(`${this.webview?.label}_data`, { sys_info: this.sysInfo });
                initUnlisten();
            });
        } else {
            this.popupService.toggleVisiblity(this.webview, event, this.popupOptions);
        }
    }

    protected mapCallback(callbackType: string): ((event: MouseEvent, callbackType: string) => void) | undefined {
        switch (callbackType) {
            case "toggle_label":
                return this.onCallbackLabelToggle.bind(this);
            case "json_viewer":
                return this.toggleJsonViewer.bind(this);
            default:
                return;
        }
    }

    private async queryInfo(): Promise<void> {
        await invoke("get_sys_info").then(async (info) => {
            this.sysInfo = info as SystemInformationPayload;
            this.updateLabels();

            if ((await this.webview?.isVisible()) && (this.props?.json_viewer?.update_on_change ?? true)) {
                await emit(`${this.webview?.label}_data`, this.sysInfo);
            }
        });
    }

    private updateLabels(): void {
        try {
            this.activeLabelFormatted = tryFormatEval(this.activeLabel, { sys_info: this.sysInfo });
            this.isError = false;
            this.errorTooltip = undefined;
        } catch (error) {
            this.activeLabelFormatted = this.activeLabel;
            this.isError = true;
            this.errorTooltip = `Error formatting active label:\n\n${(error as Error).message}`;
        }
    }

    private async onCallbackLabelToggle(): Promise<void> {
        if (this.labelAlt) {
            this.showAltLabel = !this.showAltLabel;
            this.activeLabel = this.showAltLabel ? this.labelAlt : this.label;
        }
    }
}
