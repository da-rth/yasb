use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::{Manager, State, AppHandle};
use tokio::time::sleep;
use crate::widgets::BarWidget;
use crate::widgets::ConfiguredWidget;
use super::constants::{CONFIG_FILENAME, STYLES_FILENAME};
use super::tray::TRAY_HIDE_ALL;
use super::bar;
use super::configuration;
use super::watcher;


pub fn init(app: &mut tauri::App) ->  Result<(), Box<dyn std::error::Error>> {
  let config_path = configuration::get_config_file_path(CONFIG_FILENAME);
  let styles_path = configuration::get_config_file_path(STYLES_FILENAME);

  println!("[Setup] Found config: {}", config_path.display());
  println!("[Setup] Found styles: {}", styles_path.display());

  let config =  Arc::new(Mutex::new(configuration::get_config(config_path.clone())));
  let styles =  Arc::new(Mutex::new(configuration::get_styles(styles_path.clone())));

  app.manage(configuration::Config(config.clone()));
  app.manage(configuration::Styles(styles.clone()));

  let bars = config.lock().unwrap().bars.clone();
  
  for (bar_label, bar_config) in bars.clone() {
    configuration::validate_bar_label(&bar_label.as_str());

    if let Err(e) = bar::create_bars(app, &bar_label, &bar_config) {
      eprintln!("Failed to create bar(s) for bar config '{}': {:#?}", bar_label, e);
      std::process::exit(1);
    }
  }
  
  // Enable tray hide all option
  app.tray_handle().get_item(TRAY_HIDE_ALL).set_enabled(true)?;
  let app_handle: AppHandle = app.app_handle();
  
  println!("[Setup] Initalizing async runtime");
  tauri::async_runtime::spawn(async move {
    let _hotwatch = watcher::spawn_watchers(
      &app_handle,
      &config_path,
      &styles_path
    ).expect("[Error] Hotwatch failed to initialize!");

    loop {
      // println!("Background task keeping stuff alive");
      sleep(std::time::Duration::from_secs(1)).await;
    }
  });

  Ok(())
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
    super::bar::register_win32_app_bar(bar_window, &bar_label, &bar_config);
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

  // if bar_config.win_app_bar.unwrap_or(false) {
  //   super::bar::register_win32_app_bar(bar_window, &bar_label, &bar_config);
  // }

  widgets_to_render
}
