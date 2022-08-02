use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use inflector::cases::snakecase::is_snake_case;
use inflector::cases::snakecase::to_snake_case;
use serde::Deserialize;
use serde::Serialize;
use crate::widgets::ConfiguredWidget;
use rsass::{compile_scss_path, output};
use home;

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

pub fn get_config_file_path(filename: &str) -> PathBuf {
  let home_path = home::home_dir();
  
  if home_path.is_some() {
    let home_file_path = home_path.unwrap().join(CONFIG_DIR_NAME).join(filename);
    let mut absolute_path = std::env::current_dir().unwrap();
    absolute_path.push(home_file_path.clone());

    if home_file_path.exists() {
      return home_file_path;
    } else {
      println!("[Setup] Could not find '{}' in home directory. Searching src directory instead.", absolute_path.display());
    }
  } else {
    println!("[Setup] Could not find user HOME directory. Searching src directory instead.");
  }

  let src_file_path = PathBuf::from(filename);
  
  if !src_file_path.exists() {
    let mut absolute_path = std::env::current_dir().unwrap();
    absolute_path.push(src_file_path.clone());

    eprintln!("Failed to load stylesheet at: {}.\n\nPlease create a valid stylesheet file and try again.", absolute_path.display());
    std::process::exit(1)
  }

  return src_file_path;
}

pub fn validate_bar_label(bar_label: &str) -> () {
  if !is_snake_case(bar_label) {
    let snake_cased_label = to_snake_case(bar_label);
    eprintln!("Failed to initialise bar '{}':\n\nThe bar label '{}' must be written in snake_case e.g. '{}'\n\nPlease fix and try again.",
      bar_label,
      bar_label,
      snake_cased_label
    );
    std::process::exit(1);
  }
}

pub fn get_config(config_path: PathBuf) -> YasbConfig {
  let config_stream = std::fs::read_to_string(config_path.clone());
  let mut absolute_path = std::env::current_dir().unwrap();
  absolute_path.push(config_path.clone());
  
  
  if !config_path.exists() || config_stream.is_err() {
    eprintln!("[Setup] Failed to read config at: {}.\n\nPlease create a valid config file and try again.", absolute_path.display());
    std::process::exit(1);
  }

  let config: YasbConfig = match serde_yaml::from_str(&config_stream.unwrap().as_str()) {
    Ok(cfg) => cfg,
    Err(ref e) => {
      eprintln!("Failed to load {}:\n\n{}\n\nPlease fix and try again.", absolute_path.display(), e);
      std::process::exit(1);
    },
  };
  
  config
}

pub fn get_styles(styles_path: PathBuf) -> String {
  let mut absolute_path = std::env::current_dir().unwrap();
  absolute_path.push(styles_path.clone());

  let format = output::Format { style: output::Style::Compressed, .. Default::default()};
  let css_buf = match compile_scss_path(&styles_path, format) {
    Ok(v) => v,
    Err(e) => {
      eprintln!("Failed to compile stylesheet: {}", e);
      std::process::exit(1);
    }
  };

  let css_str = match std::str::from_utf8(&css_buf) {
    Ok(v) => v.to_string(),
    Err(e) => {
      eprintln!("[Setup] Failed to read stylesheet UTF-8 sequence: {}", e);
      std::process::exit(1);
    }
  };

  css_str
}
