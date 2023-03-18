import { Injectable } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { CustomCommandResponse } from "../../bindings/widget/custom/CustomCommandResponse";

@Injectable({ providedIn: "root" })
export class KomorebiService {
    private komorebicPath = "komorebic.exe";
    private komorebiTimeout = 250;

    private async execKomorebicCommand(args: string[]): Promise<CustomCommandResponse> {
        return await invoke("process_custom_command", {
            command: this.komorebicPath,
            timeout: this.komorebiTimeout,
            args,
        });
    }

    public async queryState(): Promise<any> {
        const commandResponse = await this.execKomorebicCommand(["state"]);

        if (commandResponse.status === 0 && commandResponse.stdout) {
            return JSON.parse(commandResponse.stdout);
        } else {
            return undefined;
        }
    }

    public async focusMonitorWorkspace(monitorIndex: number, wsIndex: number) {
        await this.execKomorebicCommand(["focus-monitor-workspace", `${monitorIndex}`, `${wsIndex}`]);
    }

    public async cycleActiveWorkspace(cycleType: "next" | "previous") {
        await this.execKomorebicCommand(["cycle-workspace", cycleType]);
    }

    public async setActiveWindowBorder(enable: boolean) {
        await this.execKomorebicCommand(["active-window-border", enable ? "enable" : "disable"]);
    }

    public async newWorkspace() {
        await this.execKomorebicCommand(["new-workspace"]);
    }
}
