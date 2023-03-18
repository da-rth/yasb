import { Component, OnDestroy, OnInit } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { listen, Event as TauriEvent, UnlistenFn } from "@tauri-apps/api/event";
import { currentMonitor } from "@tauri-apps/api/window";
import { KomorebiService } from "../../../services/komorebi.service";

/**
 * TODO: PROPS TO ADD
 * offline_label: 'Komorebi Offline'
 * zero_index: bool
 * hide_empty_workspaces: bool
 * show_label_on_hover: bool
 */

@Component({
    selector: "workspace-widget",
    templateUrl: "./workspace-widget.component.html",
    styleUrls: ["./workspace-widget.component.scss"],
})
export class WorkspaceWidgetComponent implements OnInit, OnDestroy {
    public useLabels = true;
    public zeroIndex = false;

    public activeWsIndex = 0;

    public workspaces?: any[];
    public eventListeners: UnlistenFn[] = [];

    public activeMonitorName?: string;
    public activeMonitorIndex?: number;
    public activeMonitor?: any;
    public state: any;

    private cycleOnScroll = true;

    constructor(private komorebiService: KomorebiService) {}

    public async ngOnInit(): Promise<void> {
        this.activeMonitorName = (await currentMonitor())?.name?.split("\\").pop();

        this.state = await this.komorebiService.queryState();
        await this.updateWorkspaces();
        await invoke("komorebi_init_event_listener");

        this.eventListeners.push(
            await listen("KomorebiOffline", async () => {
                this.state = undefined;
                await this.updateWorkspaces();
            }),
            await listen("KomorebiFocusWorkspaceNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusMonitorWorkspaceNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiMoveWorkspaceToMonitorNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusNamedWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusNamedWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiCycleFocusWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiNewWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiWorkspaceName", this.onKomorebiUpdate.bind(this))
        );
    }

    public ngOnDestroy(): void {
        for (const unlistenFn of this.eventListeners) {
            unlistenFn();
        }
    }

    public focusWorkspace(wsIndex: number): void {
        if (this.activeWsIndex !== wsIndex && this.activeMonitorIndex != undefined) {
            this.komorebiService.focusMonitorWorkspace(this.activeMonitorIndex, wsIndex);
            this.activeWsIndex = wsIndex;
        }
    }

    public onMouseWheel(event: WheelEvent): void {
        // TODO throttle to ~500ms? rxjs throttle
        if (!this.cycleOnScroll) return;

        if (event.deltaY < 0) {
            this.komorebiService.cycleActiveWorkspace("next");
        } else {
            this.komorebiService.cycleActiveWorkspace("previous");
        }
    }
    private async onKomorebiUpdate(event: TauriEvent<any>): Promise<void> {
        this.state = event.payload;
        await this.updateWorkspaces();
    }

    private async updateWorkspaces(): Promise<void> {
        this.activeMonitorIndex = this.state.monitors.elements.findIndex(
            (monitor: any) => monitor.name == this.activeMonitorName
        );

        if (this.activeMonitorIndex != undefined && this.activeMonitorIndex != -1) {
            this.activeMonitor = this.state?.monitors.elements[this.activeMonitorIndex];
            this.activeWsIndex = this.activeMonitor?.workspaces.focused;
            this.workspaces = this.activeMonitor?.workspaces.elements.map((ws: any) => {
                return {
                    name: ws.name,
                    layout: ws.layout,
                    isEmpty: ws.containers.elements.length === 0,
                };
            });
        }
    }
}
