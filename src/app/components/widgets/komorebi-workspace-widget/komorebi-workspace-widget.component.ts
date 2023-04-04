import { Component, ElementRef, OnDestroy, OnInit, ViewChild, Inject } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { listen, Event as TauriEvent, UnlistenFn } from "@tauri-apps/api/event";
import { currentMonitor } from "@tauri-apps/api/window";
import { fromEvent, Subscription, throttleTime } from "rxjs";
import { WIDGET_PROPS } from "..";
import { KomorebiService } from "../../../services/komorebi.service";
import { KomorebiWorkspaceProps } from "../../../../bindings/widget/komorebi/KomorebiWorkspaceProps";
import { scopedEval } from "../../../../utils/eval";

@Component({
    selector: "komorebi-workspace-widget",
    templateUrl: "./komorebi-workspace-widget.component.html",
    styleUrls: ["./komorebi-workspace-widget.component.scss"],
})
export class KomorebiWorkspaceWidgetComponent implements OnInit, OnDestroy {
    @ViewChild("workspaceContainer") public workspaceContainer: ElementRef;
    public workspaces?: any[];
    public komorebiState: any;

    private activeWsIndex = 0;
    private eventListeners: UnlistenFn[] = [];
    private activeMonitorName?: string;
    private activeMonitorIndex?: number;
    private activeMonitor?: any;
    private wheelEvent$?: Subscription;

    private wsLabel: string;
    private wsLabelTooltip: string;

    constructor(private komorebiService: KomorebiService, @Inject(WIDGET_PROPS) public props: KomorebiWorkspaceProps) {}

    public async ngOnInit(): Promise<void> {
        this.wsLabel = this.props.label ?? "${data.index + 1}";
        this.wsLabelTooltip = this.props.label_tooltip ?? "Workspace ${data.index + 1}";
        this.komorebiState = await this.komorebiService.queryState();

        await this.updateWorkspaces();
        await invoke("komorebi_init_event_listener");

        this.eventListeners.push(
            await listen("KomorebiOnline", this.onKomorebiOnline.bind(this)),
            await listen("KomorebiOffline", this.onKomorebiOffline.bind(this)),
            await listen("KomorebiFloatRule", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusWorkspaceNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusMonitorWorkspaceNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiMoveWorkspaceToMonitorNumber", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusNamedWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiFocusNamedWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiCycleFocusWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiNewWorkspace", this.onKomorebiUpdate.bind(this)),
            await listen("KomorebiWorkspaceName", this.onKomorebiUpdate.bind(this))
        );

        this.wheelEvent$ = fromEvent(this.workspaceContainer.nativeElement, "wheel", { passive: true })
            .pipe(throttleTime(250))
            .subscribe((e) => {
                if (!this.props.cycle_on_scroll) return;

                if ((e as WheelEvent).deltaY < 0) {
                    this.komorebiService.cycleActiveWorkspace("next");
                } else {
                    this.komorebiService.cycleActiveWorkspace("previous");
                }
            });
    }

    public ngOnDestroy(): void {
        this.wheelEvent$?.unsubscribe();

        for (const unlistenFn of this.eventListeners) {
            unlistenFn();
        }
    }

    public async focusWorkspace(wsIndex: number): Promise<void> {
        if (this.activeMonitorIndex != undefined) {
            // this.activeWsIndex = wsIndex;
            await this.komorebiService.focusMonitorWorkspace(this.activeMonitorIndex, wsIndex);
        }
    }

    public async onKomorebiOffline(): Promise<void> {
        this.komorebiState = undefined;
        await this.updateWorkspaces();
    }

    public async onKomorebiOnline(): Promise<void> {
        this.komorebiState = await this.komorebiService.queryState();
        await this.updateWorkspaces();
    }

    private async onKomorebiUpdate(event: TauriEvent<any>): Promise<void> {
        this.komorebiState = event.payload;
        await this.updateWorkspaces();
    }

    private async updateWorkspaces(): Promise<void> {
        this.activeMonitorName = (await currentMonitor())?.name?.split("\\").pop();

        this.activeMonitorIndex = this.komorebiState?.monitors.elements.findIndex(
            (monitor: any) => monitor.name == this.activeMonitorName
        );

        if (this.activeMonitorIndex != undefined && this.activeMonitorIndex != -1) {
            this.activeMonitor = this.komorebiState?.monitors.elements[this.activeMonitorIndex];
            this.activeWsIndex = this.activeMonitor?.workspaces.focused;
            this.workspaces = this.activeMonitor?.workspaces.elements;
            this.workspaces = this.activeMonitor?.workspaces.elements.map((ws: any, index: number) => {
                ws = { ...ws, index };
                return {
                    index,
                    name: ws.name,
                    isEmpty: ws.containers.elements.length === 0,
                    isActive: this.activeWsIndex === index,
                    label: this.formatWorkspaceLabel(this.wsLabel, ws),
                    labelTooltip: this.formatWorkspaceLabel(this.wsLabelTooltip, ws),
                };
            });
        } else {
            this.workspaces = [];
            this.activeMonitor = undefined;
            this.activeWsIndex = 0;
        }
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    private formatWorkspaceLabel(label: string, ws: any): string {
        try {
            // TODO find safer alternative to eval
            return scopedEval("`" + label.replace(/`/g, "\\`") + "`", { workspace: ws });
        } catch {
            return label;
        }
    }
}
