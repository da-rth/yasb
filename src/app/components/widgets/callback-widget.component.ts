import { Component, HostListener, Inject } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { ExecOptions } from "../../../bindings/widget/base/ExecOptions";
import { WidgetCallbacks } from "../../../bindings/widget/base/WidgetCallbacks";
import { tryFormatArgsEval } from "../../../utils/eval";

export interface ExecCallback {
    exec: ExecOptions;
}

@Component({ template: "" })
export abstract class CallbackWidgetComponent {
    protected execData?: any;

    constructor(@Inject("callbacks") protected callbacks?: WidgetCallbacks<any> | null) {
        this.callbacks = callbacks;
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
            await this.runCallback(event, this.callbacks.on_middle);
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

    private async runCallback(event: MouseEvent, callbackType: string | ExecCallback): Promise<void> {
        if ((callbackType as ExecCallback)?.exec) {
            await this.onCallbackExec(callbackType as ExecCallback);
        } else {
            const callbackFunc = this.mapCallback(callbackType as string);
            callbackFunc && (await callbackFunc(event, callbackType as string));
        }
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
