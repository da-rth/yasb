import { DateTimeWidgetComponent } from "./date-time-widget/date-time-widget.component";
import { UnknownWidgetComponent } from "./unknown-widget/unknown-widget.component";
import { ActiveWindowWidgetComponent } from "./active-window-widget/active-window-widget.component";
import { InjectionToken } from "@angular/core";
import { ConfiguredWidget } from "../../../bindings/widget/ConfiguredWidget";
import { SysInfoWidgetComponent } from "./sys-info-widget/sys-info-widget.component";
import { CustomWidgetComponent } from "./custom-widget/custom-widget.component";
import { KomorebiWorkspaceWidgetComponent } from "./komorebi-workspace-widget/komorebi-workspace-widget.component";

export const WIDGET_PROPS = new InjectionToken<ConfiguredWidget>("config.widget");

export default {
    ActiveWindowWidget: ActiveWindowWidgetComponent,
    CustomWidget: CustomWidgetComponent,
    DateTimeWidget: DateTimeWidgetComponent,
    SysInfoWidget: SysInfoWidgetComponent,
    UnknownWidget: UnknownWidgetComponent,
    KomorebiWorkspaceWidget: KomorebiWorkspaceWidgetComponent,
};
