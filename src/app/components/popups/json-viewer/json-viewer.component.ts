import { CommonModule } from "@angular/common";
import { ChangeDetectorRef, Component, HostListener, OnDestroy, OnInit, ViewEncapsulation } from "@angular/core";
import { emit, Event, listen, UnlistenFn } from "@tauri-apps/api/event";
import { appWindow } from "@tauri-apps/api/window";
import { NgxJsonViewerModule } from "ngx-json-viewer";
import { StylesWatcherComponent } from "../../styles-watcher.component";

export const JSON_VIEWER_DEFAULT_WIDTH = 500;
export const JSON_VIEWER_DEFAULT_HEIGHT = 260;
export const JSON_VIEWER_DEFAULT_PADDING = 10;

export interface JsonViewerProps {
    class?: string | null;
    max_depth?: number | null;
    expanded?: boolean | null;
    from_child?: string | null;
}

@Component({
    standalone: true,
    selector: "json-viewer",
    templateUrl: "./json-viewer.component.html",
    styleUrls: ["./json-viewer.component.scss"],
    imports: [NgxJsonViewerModule, CommonModule],
    encapsulation: ViewEncapsulation.None,
})
export class JsonViewerComponent extends StylesWatcherComponent implements OnInit, OnDestroy {
    public data: any;
    public maxDepth = -1;
    public expanded = true;
    public class?: string;
    public fromChild?: string;

    private dataUnlistenFn?: UnlistenFn;
    private propsUnlistenFn?: UnlistenFn;

    constructor(private cdr: ChangeDetectorRef) {
        super();
    }

    public async ngOnInit(): Promise<void> {
        super.ngOnInit();
        const dataEvent = `${appWindow.label}_data`;
        const propsEvent = `${appWindow.label}_props`;

        this.dataUnlistenFn = await listen(dataEvent, this.onNewData.bind(this));
        this.propsUnlistenFn = await listen(propsEvent, this.onNewProps.bind(this));

        await emit(`${appWindow.label}_ngOnInit`);
    }

    public async ngOnDestroy(): Promise<void> {
        await super.ngOnDestroy();
        this.dataUnlistenFn && this.dataUnlistenFn();
        this.propsUnlistenFn && this.propsUnlistenFn();
    }

    private async onNewData(event: Event<any>): Promise<void> {
        const data = event.payload;
        // TODO find alternative for eval
        this.data = this.fromChild ? eval(`${this.fromChild}`) : data;
        this.cdr.detectChanges();
    }

    private async onNewProps(event: Event<JsonViewerProps | undefined>): Promise<void> {
        this.class = event.payload?.class ?? undefined;
        this.expanded = event.payload?.expanded ?? this.expanded;
        this.maxDepth = event.payload?.max_depth ?? this.maxDepth;
        this.fromChild = event.payload?.from_child ?? undefined;
        this.cdr.detectChanges();
    }

    @HostListener("document:keydown.escape")
    protected async onEscape(): Promise<void> {
        await appWindow.hide();
    }
}
