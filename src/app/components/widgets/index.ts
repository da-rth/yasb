import { DateTimeWidgetComponent } from "./date-time-widget/date-time-widget.component";
import { TextWidgetComponent } from "./text-widget/text-widget.component";
import { UnknownWidgetComponent } from "./unknown-widget/unknown-widget.component";
import { ActiveWindowWidgetComponent } from "./active-window-widget/active-window-widget.component";
import { InjectionToken } from "@angular/core";
import { ConfiguredWidget } from "../../../bindings/widget/ConfiguredWidget";
import { SysInfoWidgetComponent } from "./sys-info-widget/sys-info-widget.component";

export const WIDGET_PROPS = new InjectionToken<ConfiguredWidget>("config.widget");

export default {
    ActiveWindowWidget: ActiveWindowWidgetComponent,
    // CustomWidget,
    DateTimeWidget: DateTimeWidgetComponent,
    TextWidget: TextWidgetComponent,
    SysInfoWidget: SysInfoWidgetComponent,
    UnknownWidget: UnknownWidgetComponent,
};
