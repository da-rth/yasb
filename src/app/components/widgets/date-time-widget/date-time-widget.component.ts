import { Component, Inject, OnInit, ViewEncapsulation } from "@angular/core";
import { WIDGET_PROPS } from "..";
import { DateTimeWidgetProps } from "../../../../bindings/widget/datetime/DateTimeWidgetProps";
import {
  CallbackWidgetComponent,
  GenericCallbackType,
} from "../callback-widget.component";
import { WidgetCallbacks } from "../../../../bindings/widget/base/WidgetCallbacks";
import { DateTimeCallbackType } from "../../../../bindings/widget/datetime/DateTimeCallbackType";

@Component({
  selector: "date-time-widget",
  templateUrl: "./date-time-widget.component.html",
  encapsulation: ViewEncapsulation.None,
})
export class DateTimeWidgetComponent
  extends CallbackWidgetComponent
  implements OnInit
{
  public dateTimeNow?: number;
  public activeFormat = "shortTime";
  public activeTimezone?: string;
  private activeFormatIndex = 0;
  private activeTimezoneIndex = 0;
  private calendarW = 300;
  private calendarH = 350;
  private calendarPadding = 10;
  private isCalendarCallbackConfigured = false;

  public constructor(@Inject(WIDGET_PROPS) public props?: DateTimeWidgetProps) {
    super(props?.callbacks as WidgetCallbacks<DateTimeCallbackType>);
    this.isCalendarCallbackConfigured = Object.values(
      this.props?.callbacks ?? {}
    ).some((c) => c === "toggle_calendar");
    this.updateFormat();
    this.updateTimezone();
    this.updateCurrentDateTime();
  }

  public async ngOnInit(): Promise<void> {
    setInterval(
      this.updateCurrentDateTime.bind(this),
      this.props?.interval ?? 1000
    );
  }

  private async toggleCalendar(event: MouseEvent): Promise<void> {
    if (!this.popupWebview && this.isCalendarCallbackConfigured) {
      await this.createPopupWindow(
        event,
        "calendar",
        this.calendarW,
        this.calendarH,
        this.calendarPadding
      );
    } else if (await this.popupWebview?.isVisible()) {
      await this.popupWebview?.hide();
    } else {
      await this.showPopupWindow(
        event,
        this.calendarW,
        this.calendarH,
        this.calendarPadding
      );
    }
  }

  protected mapCallback(
    callbackType?: GenericCallbackType
  ): ((event: MouseEvent) => void) | undefined {
    switch (callbackType) {
      case "next_format":
        return this.cycleNextFormat.bind(this);
      case "prev_format":
        return this.cyclePrevFormat.bind(this);
      case "next_timezone":
        return this.cycleNextTimezone.bind(this);
      case "prev_timezone":
        return this.cyclePrevTimezone.bind(this);
      case "toggle_calendar":
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
      this.activeFormat =
        this.props?.formats[
          ((this.activeFormatIndex % numFormats) + numFormats) % numFormats
        ];
    }
  }

  private updateTimezone(): void {
    if (this.props?.timezones) {
      const numTzs = this.props?.timezones?.length;
      this.activeTimezone =
        this.props?.timezones[
          ((this.activeTimezoneIndex % numTzs) + numTzs) % numTzs
        ];
    }
  }
}
