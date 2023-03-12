import { Component, OnDestroy, OnInit } from "@angular/core";
import { invoke } from "@tauri-apps/api";
import { listen, UnlistenFn, Event as TauriEvent } from "@tauri-apps/api/event";

@Component({ template: "" })
export abstract class StylesWatcherComponent implements OnInit, OnDestroy {
    private stylesheetElement?: HTMLElement;
    private stylesChangedUnlistener?: UnlistenFn;

    public async ngOnInit(): Promise<void> {
        this.addStylesToHead();
        this.stylesChangedUnlistener = await listen("StylesChangedEvent", this.onStylesChanged);
    }

    public async ngOnDestroy(): Promise<void> {
        if (this.stylesheetElement) {
            document.head.removeChild(this.stylesheetElement);
        }
        this.stylesChangedUnlistener && this.stylesChangedUnlistener();
    }

    private async addStylesToHead(): Promise<void> {
        this.stylesheetElement = document.createElement("style");
        this.stylesheetElement.setAttribute("type", "text/css");
        this.stylesheetElement.textContent = await invoke("retrieve_styles");
        document.head.appendChild(this.stylesheetElement);
    }

    private onStylesChanged(event: TauriEvent<string>): void {
        if (this.stylesheetElement && event.payload) {
            this.stylesheetElement.textContent = event.payload as string;
        }
    }
}
