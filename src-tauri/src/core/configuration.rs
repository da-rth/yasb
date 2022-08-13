use super::constants::CONFIG_DIR_NAME;
use crate::widgets::ConfiguredWidget;
use anyhow::{Error, Result};
use home::home_dir;
use inflector::cases::classcase::is_class_case;
use inflector::cases::kebabcase::is_kebab_case;
use inflector::cases::snakecase::{is_snake_case, to_snake_case};
use rsass::{compile_scss_path, output};
use serde::Deserialize;
use serde::Serialize;
use std::collections::HashMap;
use std::env;
use std::fs::create_dir_all;
use std::path::Path;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display)]
#[serde(rename_all = "lowercase")]
pub enum BlurEffect {
  Blur,
  Acrylic,
  Mica,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display)]
#[serde(rename_all = "lowercase")]
pub enum BarEdge {
  Top,
  Left,
  Bottom,
  Right,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct YasbConfig {
  pub bars: HashMap<String, BarConfig>,
  pub widgets: Option<HashMap<String, ConfiguredWidget>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BarConfig {
  pub thickness: Option<u32>,
  pub edge: Option<BarEdge>,
  pub screens: Option<Vec<String>>,
  pub widgets: ColumnBarWidgets,
  pub win_app_bar: Option<bool>,
  pub always_on_top: Option<bool>,
  pub blur_effect: Option<BlurEffect>,
  pub transparency: Option<bool>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ColumnBarWidgets {
  pub left: Option<Vec<String>>,
  pub middle: Option<Vec<String>>,
  pub right: Option<Vec<String>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum BarWidget {
  Configured(ConfiguredWidget),
  Default { kind: String },
}

pub struct Config(pub Arc<Mutex<YasbConfig>>);

pub struct Styles(pub Arc<Mutex<String>>);

pub fn get_configuration_file(filename: &str) -> PathBuf {
  if let Some(home_path) = home_dir() {
    // try using $XDG_CONFIG_HOME for config if it exists
    if let Ok(xdg_config_home) = env::var("XDG_CONFIG_HOME") {
      let mut xdg_config_path = Path::new(&xdg_config_home.clone()).to_path_buf();

      xdg_config_path.push(filename);

      if xdg_config_path.exists() {
        return xdg_config_path;
      }
    }

    // otherwise, try using .config
    let mut config_path = home_path;
    config_path.push(".config");
    config_path.push(CONFIG_DIR_NAME);

    // try creating config path if it doesn't exist
    if !config_path.exists() {
      create_dir_all(config_path.parent().unwrap()).unwrap_or_else(|_| {
        eprintln!("Error creating config directory");
      });
    }

    // get the actual config file path
    let mut config_file_path = config_path;
    config_file_path.push(filename);

    if config_file_path.exists() {
      config_file_path
    } else {
      // TODO: copy the defaults over instead of exiting
      eprintln!("Config file does not exist. Exiting.");
      std::process::exit(1);
    }
  } else {
    eprintln!("Could not find user $HOME directory. Exiting.");
    std::process::exit(1);
  }
}

pub fn validate_bar_label(bar_label: &str) -> String {
  if !is_snake_case(bar_label) && !is_class_case(bar_label) && !is_kebab_case(bar_label) {
    let snake_cased_label = to_snake_case(bar_label);
    log::warn!(
      "Invalid bar label '{}' provided. Converted to camel_case: '{}'",
      bar_label,
      snake_cased_label
    );
    snake_cased_label
  } else {
    bar_label.to_string()
  }
}

pub fn get_config(config_path: &PathBuf) -> Result<YasbConfig, Error> {
  let config_stream = std::fs::read_to_string(config_path)?;
  let config: YasbConfig = serde_yaml::from_str(&config_stream.as_str())?;

  Ok(config)
}

pub fn get_styles(styles_path: &PathBuf) -> Result<String, Error> {
  let format = output::Format {
    style: output::Style::Compressed,
    ..Default::default()
  };
  let css_buf = compile_scss_path(styles_path, format)?;
  let css_str = std::str::from_utf8(&css_buf)?;

  Ok(css_str.to_string())
}
