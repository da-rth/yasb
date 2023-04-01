use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/text/")]
pub struct TextWidgetProps {
    class: Option<String>,
    text: Option<String>,
}

impl Default for TextWidgetProps {
    fn default() -> TextWidgetProps {
        TextWidgetProps { class: None, text: None }
    }
}
