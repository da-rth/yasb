use serde::{Serialize, Deserialize};
use ts_rs::TS;

use super::{custom::CustomWidgetProps, datetime::DateTimeWidgetProps, text::TextWidgetProps};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(tag = "kind")]
#[ts(export, export_to = "../src/bindings/widget/")]
pub enum ConfiguredWidget {
    TextWidget(TextWidgetProps),
    DateTimeWidget(DateTimeWidgetProps),
    CustomWidget(CustomWidgetProps)
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/")]
pub struct ConfiguredWidgets {
  pub left: Vec<ConfiguredWidget>,
  pub middle: Vec<ConfiguredWidget>,
  pub right: Vec<ConfiguredWidget>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
#[serde(rename_all = "snake_case")]
pub enum CallbackEvent {
  OnLeft,
  OnMiddle,
  OnRight,
  OnHover
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(rename_all = "lowercase")]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub enum CallbackType {
  None,
  Toggle,
  Update,
  Exec(CallbackTypeExecOptions)
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct CallbackTypeExec {
  exec: CallbackTypeExecOptions
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct CallbackTypeExecOptions {
  cmd: String,
  args: Option<Vec<String>>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct WidgetCallbacks {
  on_left: Option<CallbackType>,
  on_middle: Option<CallbackType>,
  on_right: Option<CallbackType>,
  on_hover: Option<CallbackType>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub enum ConfiguredOrDefaultWidget {
  Configured(ConfiguredWidget),
  Default {
    kind: String
  }
}


#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct ConfiguredOrDefaultWidgets {
  pub left: Vec<ConfiguredOrDefaultWidget>,
  pub middle: Vec<ConfiguredOrDefaultWidget>,
  pub right: Vec<ConfiguredOrDefaultWidget>
}

impl ConfiguredOrDefaultWidgets {
  pub fn get_column(&mut self, field: &str) -> Option<&mut Vec<ConfiguredOrDefaultWidget>> {
    match field {
        "left" => Some(&mut self.left),
        "middle" => Some(&mut self.middle),
        "right" => Some(&mut self.right),
        _ => None
    }
  }
}