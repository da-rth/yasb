import { Injectable } from "@angular/core";
import { appWindow, currentMonitor, LogicalPosition, WebviewWindow } from "@tauri-apps/api/window";
import { v4 } from "uuid";
import { BarConfig } from "../../bindings/config/BarConfig";

export const DEFAULT_POPUP_WIDTH = 300;
export const DEFAULT_POPUP_HEIGHT = 350;
export const DEFAULT_POPUP_PADDING = 10;

export interface PopupOptions {
    width: number;
    height: number;
    padding: number;
}

@Injectable({ providedIn: "root" })
export class PopupService {
    constructor() {}

    public async create(event: MouseEvent, popupType: string, popupOptions: PopupOptions): Promise<WebviewWindow> {
        const barLabel = (window as any).barLabel as string;
        const popupLabel = `${barLabel}_${popupType}_popup_${v4()}`;
        const { x, y } = await this.getEventPosition(event, popupOptions);

        return new WebviewWindow(popupLabel, {
            url: `popup/${popupType}`,
            title: "yasb-popup",
            alwaysOnTop: true,
            decorations: false,
            transparent: true,
            resizable: false,
            skipTaskbar: true,
            x,
            y,
            width: popupOptions.width,
            height: popupOptions.height,
        });
    }

    public async getEventPosition(event: MouseEvent, popup: PopupOptions): Promise<{ x: number; y: number }> {
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
                    x: winPos.x / winScale + widgetCenter.x - popup.width / 2,
                    y: winPos.y / winScale - popup.height - popup.padding * 2,
                };
                break;
            case "left":
                popupPos = {
                    x: winPos.x / winScale + barConfig.thickness + popup.padding,
                    y: winPos.y / winScale + event.clientY - popup.height / 2,
                };
                break;
            case "right":
                popupPos = {
                    x: winPos.x / winScale - popup.width - popup.padding,
                    y: winPos.y / winScale + event.clientY - popup.height / 2,
                };
                break;
            default:
                popupPos = {
                    x: winPos.x / winScale + widgetCenter.x - popup.width / 2,
                    y: winPos.y / winScale + barConfig.thickness + popup.padding,
                };
                break;
        }

        if (monPos && monSize) {
            switch (barConfig.edge) {
                case "left":
                case "right": {
                    if (popupPos.y < monPos.y / winScale) {
                        popupPos.y = monPos.y / winScale;
                    } else if (popupPos.y + popup.height > (monPos.y + monSize.height) / winScale) {
                        popupPos.y = (monPos.y + monSize.height) / winScale - popup.height;
                    }
                    break;
                }
                case "bottom":
                default: {
                    if (popupPos.x < monPos.x / winScale) {
                        popupPos.x = monPos.x / winScale;
                    } else if (popupPos.x + popup.width > (monPos.x + monSize.width) / winScale) {
                        popupPos.x = (monPos.x + monSize.width) / winScale - popup.width;
                    }
                    break;
                }
            }
        }

        return popupPos;
    }

    public async toggleVisiblity(webview: WebviewWindow, event: MouseEvent, popupOptions: PopupOptions): Promise<void> {
        if (await webview?.isVisible()) {
            await webview?.hide();
        } else {
            const { x, y } = await this.getEventPosition(event, popupOptions);
            await webview?.setPosition(new LogicalPosition(x, y));
            await webview?.show();
        }
    }
}
