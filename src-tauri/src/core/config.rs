use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use inflector::cases::snakecase::is_snake_case;
use inflector::cases::snakecase::to_snake_case;
use serde::Deserialize;
use serde::Serialize;
use crate::widgets::ConfiguredWidget;
use super::constants::CONFIG_FILENAME;
use super::setup::print_setup_error;
use home;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct YasbConfig {
  pub bars: HashMap<String, BarConfig>,
  pub widgets: Option<HashMap<String, ConfiguredWidget>>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BarConfig {
  pub thickness: Option<u32>,
  pub edge: Option<BarEdge>,
  pub screens: Option<Vec<String>>,
  pub widgets: ColumnBarWidgets,
  pub win_app_bar: Option<bool>,
  pub always_on_top: Option<bool>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ColumnBarWidgets {
  pub left: Option<Vec<String>>,
  pub middle: Option<Vec<String>>,
  pub right: Option<Vec<String>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum BarEdge {
    Top,
    Left,
    Bottom,
    Right
}

pub struct Config(pub Arc<Mutex<YasbConfig>>);

fn get_config_path() -> PathBuf {
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

pub fn get_config() -> Arc<Mutex<YasbConfig>> {
  let config_path = get_config_path();
  let config_stream = std::fs::read_to_string(config_path.clone());
  let config_path_str = std::fs::canonicalize(&config_path).unwrap();
  
  if !config_path.exists() || config_stream.is_err() {
    print_setup_error(&format!("[Setup] Failed to read config at: {}.\n\nPlease create a valid config file and try again.", config_path_str.display()), false);
    std::process::exit(1);
  }

  let config: YasbConfig = match serde_yaml::from_str(&config_stream.unwrap().as_str()) {
    Ok(cfg) => {
      println!("[Setup] Found configuration: {}", config_path_str.display());
      cfg
    },
    Err(ref e) => {
      print_setup_error(&format!("Failed to load {}:\n\n{}", config_path_str.display(), e), true);
      std::process::exit(1);
    },
  };

  Arc::new(Mutex::new(config))
}
