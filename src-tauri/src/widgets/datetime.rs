use super::base::{WidgetCallbacks, CalendarPopupOptions};
use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(rename_all = "snake_case")]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub enum DateTimeCallbackType {
    NextFormat,
    PrevFormat,
    NextTimezone,
    PrevTimezone,
    Calendar,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/datetime/")]
pub struct DateTimeWidgetProps {
    class: Option<String>,
    formats: Option<Vec<String>>,
    timezones: Option<Vec<String>>,
    interval: Option<u32>,
    calendar: Option<CalendarPopupOptions>,
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
