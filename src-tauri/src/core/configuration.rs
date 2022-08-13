use super::constants::CONFIG_DIR_NAME;
use crate::core::constants::APP_LOG_FILENAME;
use crate::widgets::base::ConfiguredWidget;
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
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/config/")]
pub struct YasbConfig {
    pub bars: HashMap<String, BarConfig>,
    pub widgets: Option<HashMap<String, ConfiguredWidget>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display, TS)]
#[serde(rename_all = "lowercase")]
#[ts(export, export_to = "../src/bindings/config/")]
pub enum BlurEffect {
    Blur,
    Acrylic,
    Mica,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, strum_macros::Display, TS)]
#[serde(rename_all = "lowercase")]
#[ts(export, export_to = "../src/bindings/config/")]
pub enum BarEdge {
    Top,
    Left,
    Bottom,
    Right,
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
    pub transparency: Option<bool>,
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
    if let Some(home_path) = home_dir() {
        let mut config_path = get_xdg_or_home_config_path(home_path.clone());
        let mut is_config_path_program_path = false;

        // If neither directory existsm try get default directories for log and configuration files
        if !config_path.exists() {
            match create_dir_all(&config_path) {
                Ok(_) => {},
                Err(e) => {
                    // Default log directory is $HOME
                    // Default configuration file directory is where the program executable lives e.g. C:\Program Files\yasb\
                    let default_path =  if filename == APP_LOG_FILENAME {  home_path.clone() } else { get_program_path() };
                    eprintln!("The directory {} could not be created. Error: {}. Defaulting to: {}", config_path.clone().display(), e, default_path.clone().display());
                    config_path = default_path;
                    is_config_path_program_path = true;
                }
            };
        }

        // Get full path to configuration file
        let mut config_file_path = config_path.clone();
        config_file_path.push(filename);
  
        // If configuration file is a (possibly nonexistant) path to a log file or exists, return the path
        if filename == APP_LOG_FILENAME || config_file_path.exists() {
            return config_file_path
        } else {
            // If we have fallen back to the program configuration path and the default configuration file doesn't exist, exit.
            if is_config_path_program_path {
                log::error!("The default for {} does not exist in {}. Exiting.", filename, config_file_path.display());
                std::process::exit(1);
            }

            // Otherwise, try copy from the default configuration file to the non-existing configuration file path
            let default_file_path = get_default_configuration_file(filename);
            match std::fs::copy(&default_file_path, &config_file_path) {
                Ok(_) => {
                    log::info!("Successfully copied {} to {}", default_file_path.display(), config_file_path.display());
                    return config_file_path;
                }
                Err(e) => {
                    log::error!("Failed copying {} to {} directory: {}.\n\nExiting.", filename, config_file_path.display(), e);
                    std::process::exit(1);
                }
            }
        }
    } else {
        eprintln!("Could not find user $HOME directory. Exiting.");
        std::process::exit(1);
    }
}

fn get_xdg_or_home_config_path(home_path: PathBuf) -> PathBuf {
    match env::var("XDG_CONFIG_HOME") {
        Ok(xdg_path) => {
            let mut xdg_config_path = Path::new(&xdg_path.clone()).to_path_buf();
            xdg_config_path.push(CONFIG_DIR_NAME);
            xdg_config_path
        },
        Err(_) => {
            let mut home_config_path = home_path;
            home_config_path.push(".config");
            home_config_path.push(CONFIG_DIR_NAME);
            home_config_path
        }
    }
}

fn get_program_path() -> PathBuf {
     match std::env::current_exe() {
        Ok(mut exe_path) => {
            exe_path.pop();
            exe_path
        },
        Err(e) => {
            log::error!("Failed loading default configuration files. Cannot find program path: {}.", e);
            std::process::exit(1);
        },
    }
}


fn get_default_configuration_file(filename: &str) -> PathBuf {
    let mut default_file_path = get_program_path();
    default_file_path.push(filename);

    if default_file_path.exists() {
        return default_file_path;
    } else {
        log::error!("The default for {} does not exist in {}. Exiting.", filename, default_file_path.display());
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
