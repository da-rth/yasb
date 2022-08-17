use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/datetime/")]
pub struct DateTimeWidgetProps {
    class: Option<String>,
    format: Option<String>,
    interval: Option<u32>,
}

impl Default for DateTimeWidgetProps {
    fn default() -> DateTimeWidgetProps {
        DateTimeWidgetProps {
            class: None,
            format: None,
            interval: None,
        }
    }
}
