use serde::{Serialize, Deserialize};


#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CallbackType {
  None,
  Toggle,
  Update,
  Exec {
    cmd: String,
    args: Option<Vec<String>>
  }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WidgetCallbacks {
  on_left: Option<CallbackType>,
  on_middle: Option<CallbackType>,
  on_right: Option<CallbackType>,
  on_hover: Option<CallbackType>
}
