use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use inflector::cases::classcase::{is_class_case};
use inflector::cases::kebabcase::is_kebab_case;
use inflector::cases::snakecase::{is_snake_case, to_snake_case};
use serde::Deserialize;
use serde::Serialize;
use home::home_dir;
use rsass::{compile_scss_path, output};
use anyhow::{Result, Error};
use ts_rs::TS;
use crate::widgets::base::ConfiguredWidget;
use super::constants::CONFIG_DIR_NAME;


#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/config/")]
pub struct YasbConfig {
  pub bars: HashMap<String, BarConfig>,
  pub widgets: Option<HashMap<String, ConfiguredWidget>>
}


#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display, TS)]
#[serde(rename_all = "lowercase")]
#[ts(export, export_to = "../src/bindings/config/")]
pub enum BlurEffect {
  Blur,
  Acrylic,
  Mica
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display, TS)]
#[serde(rename_all = "lowercase")]
#[ts(export, export_to = "../src/bindings/config/")]
pub enum BarEdge {
    Top,
    Left,
    Bottom,
    Right
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/config/")]
pub struct BarConfig {
  pub thickness: Option<u32>,
  pub edge: Option<BarEdge>,
  pub screens: Option<Vec<String>>,
  pub widgets: ColumnBarWidgets,
  pub win_app_bar: Option<bool>,
  pub always_on_top: Option<bool>,
  pub blur_effect: Option<BlurEffect>,
  pub transparency: Option<bool>
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/config/")]
pub struct ColumnBarWidgets {
  pub left: Option<Vec<String>>,
  pub middle: Option<Vec<String>>,
  pub right: Option<Vec<String>>,
}

pub struct Config(pub Arc<Mutex<YasbConfig>>);

pub struct Styles(pub Arc<Mutex<String>>);


pub fn get_configuration_file(filename: &str) -> PathBuf {
  let home_path = home_dir();
  
  if home_path.is_some() {
    let home_file_path = home_path.unwrap().join(CONFIG_DIR_NAME).join(filename);
    let mut absolute_path = std::env::current_dir().unwrap();
    absolute_path.push(home_file_path.clone());

    if home_file_path.exists() {
      return home_file_path;
    }
  } else {
    log::warn!("Could not find user HOME directory. Searching src directory instead.");
  }

  let exe_path = match std::env::current_exe() {
    Ok(exe_path) => exe_path,
    Err(e) => {
      log::error!("Failed to get current exe path: {}", e);
      std::process::exit(1);
    },
  };

  let mut src_file_path = exe_path.clone();
  src_file_path.pop();
  src_file_path.push(filename);
  
  if !src_file_path.exists() {
    let mut absolute_path = std::env::current_dir().unwrap();
    absolute_path.push(src_file_path.clone());

    log::error!("Failed to load '{}' at: {}. Please create and configure a valid '{}' file and try again.", filename, absolute_path.display(), filename);
    std::process::exit(1)
  }

  return src_file_path;
}

pub fn validate_bar_label(bar_label: &str) -> String {
  if !is_snake_case(bar_label) && !is_class_case(bar_label) &&!is_kebab_case(bar_label) {
    let snake_cased_label = to_snake_case(bar_label);
    log::warn!("Invalid bar label '{}' provided. Converted to camel_case: '{}'", bar_label, snake_cased_label);
    snake_cased_label
  } else {
    bar_label.to_string()
  }
}

pub fn get_config(config_path: &PathBuf) -> Result<YasbConfig, Error> {
  let mut absolute_path = std::env::current_dir()?;
  absolute_path.push(config_path);

  let config_stream = std::fs::read_to_string(config_path)?;
  let config: YasbConfig = serde_yaml::from_str(&config_stream.as_str())?;

  Ok(config)
}

pub fn get_styles(styles_path: &PathBuf) -> Result<String, Error> {
  let mut absolute_path = std::env::current_dir()?;
  absolute_path.push(styles_path);

  let format = output::Format { style: output::Style::Compressed, .. Default::default()};
  let css_buf = compile_scss_path(styles_path, format)?;
  let css_str = std::str::from_utf8(&css_buf)?;

  Ok(css_str.to_string())
}
