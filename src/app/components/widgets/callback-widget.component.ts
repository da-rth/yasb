import { Component, HostListener, Inject, OnDestroy } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { emit, listen } from "@tauri-apps/api/event";
import {
  appWindow,
  currentMonitor,
  LogicalPosition,
  WebviewWindow,
  WindowOptions,
} from "@tauri-apps/api/window";
import { v4 } from "uuid";
import { BarConfig } from "../../../bindings/config/BarConfig";
import { ExecOptions } from "../../../bindings/widget/base/ExecOptions";
import { WidgetCallbacks } from "../../../bindings/widget/base/WidgetCallbacks";
import { tryFormatArgsEval } from "../../../utils/format";
import { JsonViewerProps } from "../popups/json-viewer/json-viewer.component";

export interface ExecCallback {
  exec: ExecOptions;
}

export type GenericCallbackType = string | ExecCallback | null | undefined;

export interface PopupWindowOptions {
  width: number;
  height: number;
  padding: number;
}

const DEFAULT_POPUP_WIDTH = 300;
const DEFAULT_POPUP_HEIGHT = 350;
const DEFAULT_POPUP_PADDING = 10;

@Component({ template: "" })
export abstract class CallbackWidgetComponent implements OnDestroy {
  protected execData?: any;
  protected popupWebview?: WebviewWindow;
  protected popupWindowOptions?: PopupWindowOptions;
  protected jsonViewerData?: any;
  protected jsonViewerProps?: JsonViewerProps | null;

  constructor(
    @Inject("callbacks") protected callbacks?: WidgetCallbacks<any> | null
  ) {
    this.callbacks = callbacks;
  }

  public async ngOnDestroy(): Promise<void> {
    await this.popupWebview?.close();
  }

  protected abstract mapCallback(
    callbackType: string
  ): ((event: MouseEvent, callbackType: string) => void) | undefined;

  protected isCallbackTypePresent(callbackType: string): boolean {
    return Object.values(this.callbacks ?? {}).some((c) => c === callbackType);
  }

  @HostListener("click", ["$event"])
  protected async onLeftClick(event: MouseEvent): Promise<void> {
    if (this.callbacks?.on_left) {
      await this.runCallback(event, this.callbacks.on_left);
    }
  }

  @HostListener("middleclick", ["$event"])
  protected async onMiddleClick(event: MouseEvent): Promise<void> {
    if (this.callbacks?.on_middle) {
      await this.runCallback(event, this.callbacks.on_left);
    }
  }

  @HostListener("contextmenu", ["$event"])
  protected async onRightClick(event: MouseEvent): Promise<void> {
    if (this.callbacks?.on_right) {
      await this.runCallback(event, this.callbacks.on_right);
    }
  }

  @HostListener("mouseenter", ["$event"])
  protected async onHover(event: MouseEvent): Promise<void> {
    if (this.callbacks?.on_hover) {
      await this.runCallback(event, this.callbacks.on_hover);
    }
  }

  @HostListener("mouseleave", ["$event"])
  protected async onHoverLeave(event: MouseEvent): Promise<void> {
    if (
      this.callbacks?.on_hover &&
      typeof this.callbacks?.on_hover === "string" &&
      (this.callbacks.on_hover as string).startsWith("toggle")
    ) {
      await this.runCallback(event, this.callbacks.on_hover);
    }
  }

  private async runCallback(
    event: MouseEvent,
    callbackType: GenericCallbackType
  ): Promise<void> {
    if ((callbackType as ExecCallback)?.exec) {
      await this.onCallbackExec(callbackType as ExecCallback);
    } else {
      const callbackFunc = this.mapCallback(this.callbacks?.on_left as string);

      callbackFunc && (await callbackFunc(event, this.callbacks?.on_left));
    }
  }

  protected async createPopupWindow(
    event: MouseEvent,
    popupType: string
  ): Promise<void> {
    if (!this.popupWindowOptions) return;

    const barLabel = (window as any).barLabel as string;
    const popupLabel = `${barLabel}_${popupType}_popup_${v4()}`;
    const { x, y } = await this.getWidgetPopupPosition(
      event,
      this.popupWindowOptions.width,
      this.popupWindowOptions.height,
      this.popupWindowOptions.padding
    );
    this.popupWebview = new WebviewWindow(popupLabel, {
      url: `popup/${popupType}`,
      title: "yasb-popup",
      alwaysOnTop: true,
      width: this.popupWindowOptions.width,
      height: this.popupWindowOptions.height,
      x,
      y,
      decorations: false,
      transparent: true,
      resizable: false,
      skipTaskbar: true,
    } as WindowOptions);

    await listen(`${popupLabel}_init`, async () => {
      await emit(`${popupLabel}_props`, this.jsonViewerProps);
      await emit(`${popupLabel}_data`, this.jsonViewerData);
    });
  }

  protected async showPopupWindow(event: MouseEvent): Promise<void> {
    const { x, y } = await this.getWidgetPopupPosition(
      event,
      this.popupWindowOptions?.width ?? DEFAULT_POPUP_WIDTH,
      this.popupWindowOptions?.height ?? DEFAULT_POPUP_HEIGHT,
      this.popupWindowOptions?.padding ?? DEFAULT_POPUP_PADDING
    );
    await this.popupWebview?.setPosition(new LogicalPosition(x, y));
    await this.popupWebview?.show();
  }

  protected async toggleJsonViewer(event: MouseEvent): Promise<void> {
    if (!this.popupWebview && this.isCallbackTypePresent("json_viewer")) {
      await this.createPopupWindow(event, "json-viewer");
    } else if (await this.popupWebview?.isVisible()) {
      await this.popupWebview?.hide();
    } else if (this.popupWebview) {
      await emit(`${this.popupWebview?.label}_data`, this.jsonViewerData).then(
        async () => {
          await this.showPopupWindow(event);
        }
      );
    }
  }

  protected async getWidgetPopupPosition(
    event: MouseEvent,
    popupW: number,
    popupH: number,
    popupPadding: number
  ): Promise<any> {
    const winPos = await appWindow.outerPosition();
    const winScale = await appWindow.scaleFactor();

    const monitor = await currentMonitor();
    const monPos = monitor?.position;
    const monSize = monitor?.size;

    const barConfig = (window as any).barConfig as BarConfig;
    const widgetRect = (event.target as HTMLElement).getBoundingClientRect();
    const widgetCenter = {
      x: widgetRect.x + widgetRect.width / 2,
      y: widgetRect.y + widgetRect.height / 2,
    };

    let popupPos;

    switch (barConfig.edge) {
      case "bottom":
        popupPos = {
          x: winPos.x / winScale + widgetCenter.x - popupW / 2,
          y: winPos.y / winScale - popupH - popupPadding * 2,
        };
        break;
      case "left":
        popupPos = {
          x: winPos.x / winScale + barConfig.thickness + popupPadding,
          y: winPos.y / winScale + event.clientY - popupH / 2,
        };
        break;
      case "right":
        popupPos = {
          x: winPos.x / winScale - popupPadding - popupW,
          y: winPos.y / winScale + event.clientY - popupH / 2,
        };
        break;
      default: // "top" | null
        popupPos = {
          x: winPos.x / winScale + widgetCenter.x - popupW / 2,
          y: winPos.y / winScale + barConfig.thickness + popupPadding,
        };
        break;
    }

    if (monPos && monSize) {
      switch (barConfig.edge) {
        case "left":
        case "right": {
          if (popupPos.y < monPos.y / winScale) {
            popupPos.y = monPos.y / winScale;
          } else if (
            popupPos.y + popupH >
            (monPos.y + monSize.height) / winScale
          ) {
            popupPos.y = (monPos.y + monSize.height) / winScale - popupH;
          }
          break;
        }
        case "bottom":
        default: {
          if (popupPos.x < monPos.x / winScale) {
            popupPos.x = monPos.x / winScale;
          } else if (
            popupPos.x + popupW >
            (monPos.x + monSize.width) / winScale
          ) {
            popupPos.x = (monPos.x + monSize.width) / winScale - popupW;
          }
          break;
        }
      }
    }

    return popupPos;
  }

  public async onCallbackExec(execCallback?: ExecCallback): Promise<void> {
    if (this.execData && execCallback?.exec) {
      const command = execCallback.exec.cmd;
      const commandArgs = execCallback.exec?.args ?? [];
      const formattedArgs = tryFormatArgsEval(commandArgs, this.execData);
      await invoke("process_custom_command", {
        command,
        args: formattedArgs,
        timeout: 1000,
      });
    }
  }
}
