use serde::{Deserialize, Serialize};
use std::str::FromStr;
use ts_rs::TS;

use super::{
    active_window::ActiveWindowWidgetProps, custom::CustomWidgetProps,
    datetime::DateTimeWidgetProps, sys_info::SysInfoWidgetProps, text::TextWidgetProps,
    unknown::UnknownWidgetProps,
};

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[serde(tag = "kind")]
#[ts(export, export_to = "../src/bindings/widget/")]
pub enum ConfiguredWidget {
    ActiveWindowWidget(ActiveWindowWidgetProps),
    CustomWidget(CustomWidgetProps),
    DateTimeWidget(DateTimeWidgetProps),
    TextWidget(TextWidgetProps),
    SysInfoWidget(SysInfoWidgetProps),
    UnknownWidget(UnknownWidgetProps),
}

impl FromStr for ConfiguredWidget {
    type Err = ();

    fn from_str(input: &str) -> Result<ConfiguredWidget, Self::Err> {
        match input {
            "ActiveWindowWidget" => Ok(ConfiguredWidget::ActiveWindowWidget(
                ActiveWindowWidgetProps::default(),
            )),
            "CustomWidget" => Ok(ConfiguredWidget::CustomWidget(CustomWidgetProps::default())),
            "DateTimeWidget" => Ok(ConfiguredWidget::DateTimeWidget(
                DateTimeWidgetProps::default(),
            )),
            "SysInfoWidget" => Ok(ConfiguredWidget::SysInfoWidget(
                SysInfoWidgetProps::default(),
            )),
            "TextWidget" => Ok(ConfiguredWidget::TextWidget(TextWidgetProps::default())),
            _ => Err(()),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/")]
pub struct ConfiguredWidgets {
    pub left: Vec<ConfiguredWidget>,
    pub middle: Vec<ConfiguredWidget>,
    pub right: Vec<ConfiguredWidget>,
}

impl ConfiguredWidgets {
    pub fn get_column(&mut self, field: &str) -> Option<&mut Vec<ConfiguredWidget>> {
        match field {
            "left" => Some(&mut self.left),
            "middle" => Some(&mut self.middle),
            "right" => Some(&mut self.right),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
#[serde(rename_all = "snake_case")]
pub enum CallbackEvent {
    OnLeft,
    OnMiddle,
    OnRight,
    OnHover,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct ExecOptions {
    cmd: String,
    args: Option<Vec<String>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct WidgetCallbacks<T> {
    on_left: Option<T>,
    on_middle: Option<T>,
    on_right: Option<T>,
    on_hover: Option<T>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct JsonViewerPopupOptions {
    pub width: Option<u32>,
    pub height: Option<u32>,
    pub padding: Option<u32>,
    pub class: Option<String>,
    pub max_depth: Option<u32>,
    pub expanded: Option<bool>,
    pub from_child: Option<String>,
    pub update_on_change: Option<bool>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/base/")]
pub struct CalendarPopupOptions {
    pub width: Option<u32>,
    pub height: Option<u32>,
    pub padding: Option<u32>,
    pub class: Option<String>,
    pub locale: Option<String>,
}
