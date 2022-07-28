use std::path::PathBuf;
use home;
use inflector::cases::snakecase::is_snake_case;
use inflector::cases::snakecase::to_snake_case;
use serde::Deserialize;
use serde::Serialize;
use super::constants::CONFIG_FILENAME;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct YasbConfig {
  pub bars: Vec<BarConfig>,
  pub widgets: Option<Vec<WidgetConfig>>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BarConfig {
  pub label: String,
  pub thickness: Option<u32>,
  pub edge: Option<BarEdge>,
  pub screens: Option<Vec<String>>,
  pub widgets: Option<ActiveBarWidgets>,
  pub win_app_bar: Option<bool>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WidgetConfig {
  pub name: String
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum BarEdge {
    Top,
    Left,
    Bottom,
    Right
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ActiveBarWidgets {
  pub left: Option<Vec<String>>,
  pub middle: Option<Vec<String>>,
  pub right: Option<Vec<String>>,
}

pub fn get_config_path() -> PathBuf {
    let home_path = home::home_dir();

    if let Some(home_dir) = home_path {
        let home_config = home_dir.join(".yasb").join(CONFIG_FILENAME);

        if home_config.exists() {
            return home_config
        }
    }

    PathBuf::from(CONFIG_FILENAME)
}

pub fn validate_bar_label(bar_label: &str) -> () {
  if !is_snake_case(bar_label) {
    let snake_cased_label = to_snake_case(bar_label);
    eprintln!("[Error] Failed to initialise bar '{}':\n\nThe bar label '{}' must be written in snake_case e.g. '{}'\n\nPlease fix and try again.",
      bar_label,
      bar_label,
      snake_cased_label
    );
    std::process::exit(1);
  }
}
