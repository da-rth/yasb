import { Component, Inject, OnInit, ViewEncapsulation } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { emit, listen } from "@tauri-apps/api/event";
import { WebviewWindow } from "@tauri-apps/api/window";
import { WIDGET_PROPS } from "..";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import { CustomCallbackType } from "../../../../bindings/widget/custom/CustomCallbackType";
import { CustomCommandResponse } from "../../../../bindings/widget/custom/CustomCommandResponse";
import { CustomWidgetProps } from "../../../../bindings/widget/custom/CustomWidgetProps";
import { tryFormatEval } from "../../../../utils/eval";
import { PopupOptions, PopupService } from "../../../services/popup.service";
import {
    JSON_VIEWER_DEFAULT_HEIGHT,
    JSON_VIEWER_DEFAULT_PADDING,
    JSON_VIEWER_DEFAULT_WIDTH,
} from "../../popups/json-viewer/json-viewer.component";
import { CallbackWidgetComponent } from "../callback-widget.component";

const DEFAULT_LABEL = "CustomWidget";

@Component({
    selector: "custom-widget",
    templateUrl: "./custom-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class CustomWidgetComponent extends CallbackWidgetComponent implements OnInit {
    public isHidden = true;
    public isError = false;
    public activeLabelFormatted?: string;
    public errorTooltip?: string;

    private label: string;
    private labelAlt?: string;
    private commandResult?: CustomCommandResponse;
    private commandResultData?: any;
    private showAltLabel = false;
    private activeLabel: string;
    private webview: WebviewWindow;
    private popupOptions: PopupOptions;

    constructor(private popupService: PopupService, @Inject(WIDGET_PROPS) public props?: CustomWidgetProps) {
        super(props?.callbacks as WidgetCallbacks<CustomCallbackType>);
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
        await this.executeCustomCommand();
        this.props?.interval && setInterval(this.executeCustomCommand.bind(this), this.props?.interval);
    }

    private async executeCustomCommand() {
        if (this.props?.command) {
            this.commandResult = await invoke("process_custom_command", {
                command: this.props.command?.cmd,
                args: this.props.command?.args ?? [],
                timeout: Math.floor((this.props.command?.interval ?? 1000) / 2),
            });
        }

        this.updateLabels();
    }

    private async toggleJsonViewer(event: MouseEvent): Promise<void> {
        if (!this.webview && this.isCallbackTypePresent("json_viewer")) {
            this.webview = await this.popupService.create(event, "json_viewer", this.popupOptions);
            const initUnlisten = await listen(`${this.webview?.label}_ngOnInit`, async () => {
                await emit(`${this.webview?.label}_data`, { res: this.commandResultData });
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

    private tryFormatActiveLabel(labelToFormat: string, withCommandContext = false): void {
        try {
            this.activeLabelFormatted = tryFormatEval(
                labelToFormat,
                withCommandContext ? { res: this.commandResultData } : {}
            );
            this.isError = false;
        } catch (error) {
            this.activeLabelFormatted = labelToFormat;
            this.errorTooltip = `Error formatting label:\n\n${(error as Error).message}`;
            this.isError = true;
        }
    }

    private updateLabels(): void {
        if (this.commandResult?.stdout) {
            try {
                this.commandResultData = JSON.parse(this.commandResult.stdout);
            } catch {
                this.commandResultData = this.commandResult.stdout.replace("\n", "\\n");
            }
            this.tryFormatActiveLabel(this.activeLabel, true);
        } else {
            const cmd = this.props?.command?.cmd;

            if (cmd) {
                // If no stdout, format error tooltip
                const args = ` - ${(this.props?.command?.args ?? []).join("\n")}`;
                const status = this.commandResult?.status ?? 1;
                this.errorTooltip =
                    `The command '${cmd}' exited with code ${status}\n\n` +
                    (this.props?.command?.args ? `args:\n${args}` : "") +
                    `\n\nstderr: ${this.commandResult?.stderr ?? "None"}`;
                this.tryFormatActiveLabel(cmd, false);
                this.isError = true;
            } else {
                this.tryFormatActiveLabel(this.activeLabel, false);
            }
        }
    }

    private async onCallbackLabelToggle(): Promise<void> {
        if (this.labelAlt) {
            this.showAltLabel = !this.showAltLabel;
            this.activeLabel = this.showAltLabel ? this.labelAlt : this.label;
            this.updateLabels();
        }
    }
}
