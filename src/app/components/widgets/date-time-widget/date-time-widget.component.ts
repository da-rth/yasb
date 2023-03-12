import { Component, Inject, OnInit, ViewEncapsulation } from "@angular/core";
import { WIDGET_PROPS } from "..";
import { DateTimeWidgetProps } from "../../../../bindings/widget/datetime/DateTimeWidgetProps";
import { CallbackWidgetComponent } from "../callback-widget.component";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import { DateTimeCallbackType } from "../../../../bindings/widget/datetime/DateTimeCallbackType";
import {
    CALENDAR_DEFAULT_HEIGHT,
    CALENDAR_DEFAULT_PADDING,
    CALENDAR_DEFAULT_WIDTH,
} from "../../popups/calendar/calendar.component";
import { PopupOptions, PopupService } from "../../../services/popup.service";
import { WebviewWindow } from "@tauri-apps/api/window";

@Component({
    selector: "date-time-widget",
    templateUrl: "./date-time-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class DateTimeWidgetComponent extends CallbackWidgetComponent implements OnInit {
    public dateTimeNow?: number;
    public activeFormat = "shortTime";
    public activeTimezone?: string;
    private activeFormatIndex = 0;
    private activeTimezoneIndex = 0;
    private webview: WebviewWindow;
    private popupOptions: PopupOptions;

    public constructor(private popupService: PopupService, @Inject(WIDGET_PROPS) public props?: DateTimeWidgetProps) {
        super(props?.callbacks as WidgetCallbacks<DateTimeCallbackType>);
        this.updateFormat();
        this.updateTimezone();
        this.updateCurrentDateTime();
        this.popupOptions = {
            width: this.props?.calendar?.width ?? CALENDAR_DEFAULT_WIDTH,
            height: this.props?.calendar?.height ?? CALENDAR_DEFAULT_HEIGHT,
            padding: this.props?.calendar?.padding ?? CALENDAR_DEFAULT_PADDING,
        };
    }

    public async ngOnInit(): Promise<void> {
        setInterval(this.updateCurrentDateTime.bind(this), this.props?.interval ?? 1000);
    }

    private async toggleCalendar(event: MouseEvent): Promise<void> {
        if (!this.webview && this.isCallbackTypePresent("calendar")) {
            this.webview = await this.popupService.create(event, "calendar", this.popupOptions);
        } else {
            this.popupService.toggleVisiblity(this.webview, event, this.popupOptions);
        }
    }

    protected mapCallback(callbackType?: string): ((event: MouseEvent) => void) | undefined {
        switch (callbackType) {
            case "next_format":
                return this.cycleNextFormat.bind(this);
            case "prev_format":
                return this.cyclePrevFormat.bind(this);
            case "next_timezone":
                return this.cycleNextTimezone.bind(this);
            case "prev_timezone":
                return this.cyclePrevTimezone.bind(this);
            case "calendar":
                return this.toggleCalendar.bind(this);
            default:
                return;
        }
    }

    private updateCurrentDateTime(): void {
        this.dateTimeNow = Date.now();
    }

    private cycleNextFormat(): void {
        this.activeFormatIndex++;
        this.updateFormat();
    }

    private cyclePrevFormat(): void {
        this.activeFormatIndex--;
        this.updateFormat;
    }

    private cycleNextTimezone(): void {
        this.activeTimezoneIndex++;
        this.updateTimezone();
    }

    private cyclePrevTimezone(): void {
        this.activeTimezoneIndex--;
        this.updateTimezone;
    }

    private updateFormat(): void {
        if (this.props?.formats) {
            const numFormats = this.props?.formats?.length;
            this.activeFormat = this.props?.formats[((this.activeFormatIndex % numFormats) + numFormats) % numFormats];
        }
    }

    private updateTimezone(): void {
        if (this.props?.timezones) {
            const numTzs = this.props?.timezones?.length;
            this.activeTimezone = this.props?.timezones[((this.activeTimezoneIndex % numTzs) + numTzs) % numTzs];
        }
    }
}
