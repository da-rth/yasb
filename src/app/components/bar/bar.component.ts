import {
  Component,
  Injector,
  OnDestroy,
  OnInit,
  ViewEncapsulation,
} from "@angular/core";
import { appWindow } from "@tauri-apps/api/window";
import { UnlistenFn, listen } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/tauri";
import { BarConfig } from "../../../bindings/config/BarConfig";
import { ConfiguredWidgets } from "../../../bindings/widget/ConfiguredWidgets";
import { ConfiguredWidget } from "../../../bindings/widget/ConfiguredWidget";
import { StylesWatcherComponent } from "../styles-watcher.component";
import Widgets, { WIDGET_PROPS } from "./../../components/widgets";
import log from "../../../utils/log";

@Component({
  selector: "yasb-bar",
  templateUrl: "./bar.component.html",
  styleUrls: ["./bar.component.scss"],
  encapsulation: ViewEncapsulation.None,
})
export class BarComponent
  extends StylesWatcherComponent
  implements OnInit, OnDestroy
{
  private windowHiddenByuser = false;
  private eventListeners: UnlistenFn[] = [];
  private barConfig: BarConfig;

  public widgets = Widgets;
  public barWidgets: ConfiguredWidgets = { left: [], middle: [], right: [] };
  public barLabel?: string;

  constructor(private injector: Injector) {
    super();
  }

  public get edgeClass(): string {
    return `edge-${this.barConfig?.edge}`;
  }

  public async ngOnInit(): Promise<void> {
    await super.ngOnInit();

    const barLabel = appWindow.label.slice(0, appWindow.label.lastIndexOf("_"));
    this.barWidgets = await invoke("retrieve_widgets", { barLabel });
    this.barConfig = await invoke("retrieve_config", { barLabel });
    this.barLabel = barLabel;

    (window as any).barConfig = this.barConfig;
    (window as any).barLabel = this.barLabel;

    // Create props injector(s) for configured widgets
    for (const col of Object.keys(this.barWidgets) as Array<
      keyof typeof this.barWidgets
    >) {
      this.barWidgets[col] = this.barWidgets[col].map(
        (widget: ConfiguredWidget) => ({
          injector: this.createPropsInjector(widget),
          ...widget,
        })
      ) as ConfiguredWidget[];
    }

    await this.addEventListeners();
    await appWindow.show();
    await appWindow.setAlwaysOnTop(this.barConfig?.always_on_top ?? false);
    await log.info(`${appWindow.label} mounted.`);
  }

  public async ngOnDestroy(): Promise<void> {
    await super.ngOnDestroy();
    await this.unregisterEventListeners();
  }

  public createPropsInjector(widgetProps: ConfiguredWidget): Injector {
    return Injector.create({
      providers: [{ provide: WIDGET_PROPS, useValue: widgetProps }],
      parent: this.injector,
    });
  }

  public getWidgetComponent(widget: ConfiguredWidget): any {
    return widget.kind in this.widgets
      ? (this.widgets as any)[widget.kind]
      : this.widgets.UnknownWidget;
  }

  public getInjector(widgetProps: ConfiguredWidget): Injector {
    return (widgetProps as any).injector as Injector;
  }

  private async addEventListeners(): Promise<void> {
    this.eventListeners.push(
      await listen("HideAllWindowsEvent", this.onHideAllWindows)
    );
    this.eventListeners.push(
      await listen("ShowAllWindowsEvent", this.onShowAllWindows)
    );
    this.eventListeners.push(
      await listen("FullscreenHideWindow", this.onHideFullscreen)
    );
    this.eventListeners.push(
      await listen("FullscreenShowWindow", this.onShowFullscreen)
    );
  }

  private async unregisterEventListeners(): Promise<void> {
    for (const unlistenFn of this.eventListeners) {
      unlistenFn();
    }
  }

  private onHideAllWindows(): void {
    this.windowHiddenByuser = true;
    appWindow.hide();
  }

  private onShowAllWindows(): void {
    this.windowHiddenByuser = false;
    appWindow.show();
  }

  private onHideFullscreen(): void {
    if (this.barConfig?.always_on_top && !this.windowHiddenByuser) {
      appWindow.hide();
    }
  }

  private onShowFullscreen(): void {
    if (this.barConfig?.always_on_top && !this.windowHiddenByuser) {
      appWindow.show();
    }
  }
}
