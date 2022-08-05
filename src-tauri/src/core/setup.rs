use std::collections::HashMap;
use std::path::{PathBuf};
use std::sync::{Arc, Mutex};
use tauri::{Manager, State, AppHandle};
use tokio::time::sleep;
use std::fs::canonicalize;
use std::fs::File;
use simplelog::{
  CombinedLogger,
  TermLogger,
  WriteLogger,
  Config,
  LevelFilter, TerminalMode, ColorChoice
};
use crate::core::constants::APP_LOG_FILENAME;
use crate::widgets::BarWidget;
use crate::widgets::ConfiguredWidget;
use crate::win32::app_bar;
use super::constants::{CONFIG_FILENAME, STYLES_FILENAME};
use super::watcher;
use super::bar;
use super::configuration;

pub fn init(app: &mut tauri::App) ->  Result<(), Box<dyn std::error::Error>> {
  let app_handle = app.app_handle().clone();
  let app_name = app.config().package.product_name.clone().unwrap();
  let app_version = app.config().package.version.clone().unwrap();
  let log_path = init_logger();

  log::info!("Initialising {} v{}", app_name, app_version);
  log::info!("Logging to: {}", canonicalize(log_path)?.display().to_string().replace("\\\\?\\", ""));

  init_ctrlc_handler(app_handle.clone());

  let config_path = configuration::get_configuration_file(CONFIG_FILENAME);
  log::info!("Found config at: {}", canonicalize(config_path.clone())?.display().to_string().replace("\\\\?\\", ""));

  let styles_path = configuration::get_configuration_file(STYLES_FILENAME);
  log::info!("Found stylesheet at: {}", canonicalize(styles_path.clone())?.display().to_string().replace("\\\\?\\", ""));

  let (config, styles) = init_config_paths(&app_handle, &config_path, &styles_path);
  app_handle.manage(configuration::Config(Arc::new(Mutex::new(config.clone()))));
  app_handle.manage(configuration::Styles(Arc::new(Mutex::new(styles.clone()))));
  
  // Create the bars based on given config. Styles are set later...
  bar::create_bars_from_config(&app_handle, config);

  // Spawn background task
  tauri::async_runtime::spawn(async move {
    // Spawn file watchers for config and styles
    let _hotwatch = watcher::spawn_watchers(
      app_handle.clone(),
      config_path.clone(),
      styles_path.clone()
    ).expect("File watcher failed to initialise!");
    
    loop {
        sleep(std::time::Duration::from_secs(1)).await;
    }
  });

  Ok(())
}

fn init_logger() -> PathBuf {
  let log_path = PathBuf::from(APP_LOG_FILENAME);

  CombinedLogger::init(
    vec![
      TermLogger::new(
        LevelFilter::Info,
        Config::default(),
        TerminalMode::Mixed,
        ColorChoice::Auto
      ),
      WriteLogger::new(
        LevelFilter::Info,
        Config::default(),
        File::create(log_path.clone()).unwrap()
      )
    ]
  ).expect("Failed to initialise logger");

  log_path
}

fn init_ctrlc_handler(app_handle: AppHandle) -> () {
  ctrlc::set_handler(move || {
    log::info!("Ctrl+C detected. Cleaning up.");
    let _ = app_bar::ab_remove_all(&app_handle.windows());
    log::info!("Exiting {}. Goodbye :)", app_handle.config().package.product_name.clone().unwrap());
    app_handle.exit(0);
  }).expect("Error setting Ctrl-C handler")
}

fn init_config_paths(app_handle: &AppHandle, config_path: &PathBuf, styles_path: &PathBuf) -> (configuration::YasbConfig, String) {
  let config = match configuration::get_config(&config_path) {
    Ok(cfg) => cfg,
    Err(e) => {
      log::error!("Failed to load config: {}", e);
      app_handle.exit(1);
      std::process::exit(1);
    }
  };

  let styles = match configuration::get_styles(&styles_path) {
    Ok(styles) => styles,
    Err(e) => {
      log::error!("Failed to load stylesheet: {}", e);
      app_handle.exit(1);
      std::process::exit(1);
    }
  };

  (config, styles)
}

fn get_config_from_state(config: &State<configuration::Config>, bar_label: &str) -> configuration::BarConfig {
  let locked_config = config.0.lock().unwrap();
  locked_config.bars.get(bar_label).unwrap().clone()
}

fn get_configured_widgets_from_state(config: &State<configuration::Config>) -> HashMap<String, ConfiguredWidget> {
  let locked_config = config.0.lock().unwrap();
  locked_config.widgets.as_ref().unwrap().clone()
}

#[tauri::command]
pub fn retrieve_config(bar_label: String, bar_window: tauri::Window, config_state: State<configuration::Config>) -> configuration::BarConfig {
  let bar_config = get_config_from_state(&config_state, &bar_label.as_str());
  
  if bar_config.win_app_bar.unwrap_or(false) {
    super::bar::register_win32_app_bar(bar_window, &bar_config);
  }
  
  bar_config
}

#[tauri::command]
pub fn retrieve_styles(styles_state: State<configuration::Styles>) -> String {
  styles_state.0.lock().unwrap().to_string()
}

#[tauri::command]
pub fn retrieve_widgets(bar_label: String, config_state: State<configuration::Config>) -> HashMap<String, Vec<BarWidget>> {
  let bar_config = get_config_from_state(&config_state, &bar_label.as_str());
  let configured_widgets = get_configured_widgets_from_state(&config_state);

  let bar_widgets: HashMap<String, Option<&Vec<String>>> = HashMap::from([
    ("left".to_string(), bar_config.widgets.left.as_ref()),
    ("middle".to_string(), bar_config.widgets.middle.as_ref()),
    ("right".to_string(), bar_config.widgets.right.as_ref())
  ]);

  let mut widgets_to_render: HashMap<String, Vec<BarWidget>> = HashMap::from([
    ("left".to_string(), Vec::new()),
    ("middle".to_string(), Vec::new()),
    ("right".to_string(), Vec::new())
  ]);
  
  for (bar_column, column_widgets) in bar_widgets {
    let column_to_render = widgets_to_render.get_mut(&bar_column).unwrap();

    if column_widgets.is_some() {
      for col_widget_name in column_widgets.unwrap() {
        if configured_widgets.contains_key(col_widget_name) {
          column_to_render.push(BarWidget::Configured(configured_widgets.get(col_widget_name).unwrap().clone()));
        } else {
          column_to_render.push(BarWidget::Default { kind: col_widget_name.to_string() });
        }
      }
    }
  }

  widgets_to_render
}
