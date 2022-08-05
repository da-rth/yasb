use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use inflector::cases::snakecase::is_snake_case;
use inflector::cases::snakecase::to_snake_case;
use serde::Deserialize;
use serde::Serialize;
use home::home_dir;
use rsass::{compile_scss_path, output};
use anyhow::{Result, Error};
use crate::widgets::ConfiguredWidget;
use super::constants::CONFIG_DIR_NAME;

pub struct Config(pub Arc<Mutex<YasbConfig>>);
pub struct Styles(pub Arc<Mutex<String>>);

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

  let src_file_path = PathBuf::from(filename);
  
  if !src_file_path.exists() {
    let mut absolute_path = std::env::current_dir().unwrap();
    absolute_path.push(src_file_path.clone());

    log::error!("Failed to load '{}' at: {}. Please create and configure a valid '{}' file and try again.", filename, absolute_path.display(), filename);
    std::process::exit(1)
  }

  return src_file_path;
}

pub fn validate_bar_label(bar_label: &str) -> () {
  if !is_snake_case(bar_label) {
    let snake_cased_label = to_snake_case(bar_label);
    log::error!("Failed to initialise bar with label '{}'. The label '{}' must be in snake_case e.g. '{}'. Please fix and try again.",
      bar_label,
      bar_label,
      snake_cased_label
    );
    std::process::exit(1);
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
