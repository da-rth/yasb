use serde::{Serialize, Deserialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/text/")]
pub struct TextWidgetProps {
  class: Option<String>,
  text: Option<String>
}
