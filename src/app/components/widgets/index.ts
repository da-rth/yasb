import { DateTimeWidgetComponent } from "./date-time-widget/date-time-widget.component";
import { TextWidgetComponent } from "./text-widget/text-widget.component";
import { UnknownWidgetComponent } from "./unknown-widget/unknown-widget.component";
import { ActiveWindowWidgetComponent } from "./active-window-widget/active-window-widget.component";
import { InjectionToken } from "@angular/core";
import { ConfiguredWidget } from "../../../bindings/widget/ConfiguredWidget";
import { SysInfoWidgetComponent } from "./sys-info-widget/sys-info-widget.component";
import { CustomWidgetComponent } from "./custom-widget/custom-widget.component";
import { WorkspaceWidgetComponent } from "./workspace-widget/workspace-widget.component";

export const WIDGET_PROPS = new InjectionToken<ConfiguredWidget>("config.widget");

export default {
    ActiveWindowWidget: ActiveWindowWidgetComponent,
    CustomWidget: CustomWidgetComponent,
    DateTimeWidget: DateTimeWidgetComponent,
    SysInfoWidget: SysInfoWidgetComponent,
    TextWidget: TextWidgetComponent,
    UnknownWidget: UnknownWidgetComponent,
    WorkspaceWidget: WorkspaceWidgetComponent,
};
