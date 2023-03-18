import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { AppComponent } from "./app.component";
import { BarComponent } from "./components/bar/bar.component";
import { ActiveWindowWidgetComponent } from "./components/widgets/active-window-widget/active-window-widget.component";
import { CustomWidgetComponent } from "./components/widgets/custom-widget/custom-widget.component";
import { DateTimeWidgetComponent } from "./components/widgets/date-time-widget/date-time-widget.component";
import { SysInfoWidgetComponent } from "./components/widgets/sys-info-widget/sys-info-widget.component";
import { TextWidgetComponent } from "./components/widgets/text-widget/text-widget.component";
import { CalendarComponent } from "./components/popups/calendar/calendar.component";
import { JsonViewerComponent } from "./components/popups/json-viewer/json-viewer.component";
import { WIDGET_PROPS } from "./components/widgets";
import { WorkspaceWidgetComponent } from "./components/widgets/workspace-widget/workspace-widget.component";

@NgModule({
    declarations: [
        AppComponent,
        BarComponent,
        ActiveWindowWidgetComponent,
        CustomWidgetComponent,
        DateTimeWidgetComponent,
        SysInfoWidgetComponent,
        TextWidgetComponent,
        WorkspaceWidgetComponent,
    ],
    imports: [
        BrowserModule,
        CommonModule,
        BrowserAnimationsModule,
        RouterModule.forRoot([
            {
                path: "",
                component: BarComponent,
            },
            {
                path: "popup/calendar",
                component: CalendarComponent,
            },
            {
                path: "popup/json_viewer",
                component: JsonViewerComponent,
            },
        ]),
    ],
    exports: [CommonModule],
    providers: [{ provide: WIDGET_PROPS, useValue: true }],
    bootstrap: [AppComponent],
})
export class AppModule {}
