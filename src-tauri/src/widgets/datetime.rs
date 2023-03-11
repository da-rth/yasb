use super::base::{BasePopupProps, WidgetCallbacks};
use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(rename_all = "snake_case")]
#[ts(export, export_to = "../src/bindings/widget/datetime/")]
pub enum DateTimeCallbackType {
    NextFormat,
    PrevFormat,
    NextTimezone,
    PrevTimezone,
    ToggleCalendar,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/datetime/")]
pub struct CalendarProps {
    popup: Option<BasePopupProps>,
    locale: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/datetime/")]
pub struct DateTimeWidgetProps {
    class: Option<String>,
    formats: Option<Vec<String>>,
    timezones: Option<Vec<String>>,
    interval: Option<u32>,
    calendar: Option<CalendarProps>,
    callbacks: Option<WidgetCallbacks<DateTimeCallbackType>>,
}

impl Default for DateTimeWidgetProps {
    fn default() -> DateTimeWidgetProps {
        DateTimeWidgetProps {
            class: None,
            formats: None,
            timezones: None,
            interval: None,
            calendar: None,
            callbacks: None,
        }
    }
}
