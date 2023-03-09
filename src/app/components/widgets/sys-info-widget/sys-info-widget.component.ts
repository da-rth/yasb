import { Component, Inject, ViewEncapsulation } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { emit, listen } from "@tauri-apps/api/event";
import { WIDGET_PROPS } from "..";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import { SysInfoCallbackType } from "../../../../bindings/widget/sysinfo/SysInfoCallbackType";
import { SysInfoWidgetProps } from "../../../../bindings/widget/sysinfo/SysInfoWidgetProps";
import { SystemInformation } from "../../../../bindings/widget/sysinfo/SystemInformation";
import { tryFormatEval } from "../../../../utils/format";
import { CallbackWidgetComponent } from "../callback-widget.component";

const DEFAULT_LABEL = "hostname: ${data.sys.host}";
// TODO add json popup
// TODO emit sys info event, make single-call, unlock after data obtained, emit new data event

@Component({
  selector: "sys-info-widget",
  templateUrl: "./sys-info-widget.component.html",
  encapsulation: ViewEncapsulation.None,
})
export class SysInfoWidgetComponent
  extends CallbackWidgetComponent
  implements OnInit
{
  public isHidden = true;
  public isError = false;
  public activeLabelFormatted?: string;
  public errorTooltip?: string;

  private label: string;
  private labelAlt?: string;
  private sysInfo?: SystemInformation;
  private showAltLabel = false;
  private activeLabel: string;

  private jsonPopupWidth = 500;
  private jsonPopupHeight = 260;
  private jsonPopupPadding = 10;
  private isJsonViewerCallbackConfigured = true;

  public constructor(@Inject(WIDGET_PROPS) public props?: SysInfoWidgetProps) {
    super(props?.callbacks as WidgetCallbacks<SysInfoCallbackType>);
    this.label = this.props?.label ?? DEFAULT_LABEL;
    this.labelAlt = this.props?.label_alt ?? undefined;
    this.activeLabel = this.label;
  }

  public async ngOnInit(): Promise<void> {
    await this.queryInfo();
    this.props?.interval &&
      setInterval(this.queryInfo.bind(this), this.props.interval);
  }

  protected mapCallback(
    callbackType: string
  ): ((event: MouseEvent, callbackType: string) => void) | undefined {
    switch (callbackType) {
      case "toggle_label":
        return this.onCallbackLabelToggle.bind(this);
      case "toggle_json_viewer":
        return this.toggleJsonViewer.bind(this);
      default:
        return () => {};
    }
  }

  private async queryInfo(): Promise<void> {
    await invoke("get_sys_info").then(async (info) => {
      this.sysInfo = info as SystemInformation;
      //   if ((await this.popupWebview?.isVisible())) {
      //   await emit(`${this.popupWebview?.label}_data`, this.sysInfo);
      // }
      this.updateLabels();
    });
  }

  private updateLabels(): void {
    try {
      this.activeLabelFormatted = tryFormatEval(this.activeLabel, this.sysInfo);
      this.isError = false;
      this.errorTooltip = undefined;
    } catch (error) {
      this.activeLabelFormatted = this.activeLabel;
      this.isError = true;
      this.errorTooltip = `Error formatting active label:\n\n${
        (error as Error).message
      }`;
    }
  }

  private async onCallbackLabelToggle(): Promise<void> {
    if (this.labelAlt) {
      this.showAltLabel = !this.showAltLabel;
      this.activeLabel = this.showAltLabel ? this.labelAlt : this.label;
    }
  }

  private async toggleJsonViewer(event: MouseEvent): Promise<void> {
    if (!this.popupWebview && this.isJsonViewerCallbackConfigured) {
      await this.createPopupWindow(
        event,
        "json-viewer",
        this.jsonPopupWidth,
        this.jsonPopupHeight,
        this.jsonPopupPadding
      );
      const unlisten = await listen(
        `${(this.popupWebview as any).label}_init`,
        async () => {
          await emit(`${this.popupWebview?.label}_data`, this.sysInfo);
          unlisten();
        }
      );
    } else if (await this.popupWebview?.isVisible()) {
      await this.popupWebview?.hide();
    } else if (this.popupWebview) {
      await emit(`${this.popupWebview?.label}_data`, this.sysInfo);
      await this.showPopupWindow(
        event,
        this.jsonPopupWidth,
        this.jsonPopupHeight,
        this.jsonPopupPadding
      );
    }
  }
}
