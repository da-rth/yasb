use std::collections::HashMap;

use tauri::{Manager, State};
use crate::widgets::BarWidget;
use crate::widgets::ConfiguredWidget;

use super::config::BarConfig;
use super::config::Config;
use super::tray::TRAY_HIDE_ALL;
use super::bar;
use super::config;


pub fn print_setup_error(msg: &str, please_fix: bool) -> () {
  let please_fix_msg = "\n\nPlease fix and try again.";
  println!("[Error] {}{}", msg, if please_fix {please_fix_msg} else {""});
}

pub fn init(app: &mut tauri::App) ->  Result<(), Box<dyn std::error::Error>> {
  let config: State<'_, Config> = app.state();
  let bars = config.0.lock().unwrap().bars.clone();
  
  for (bar_label, bar_config) in bars.clone() {
    config::validate_bar_label(&bar_label.as_str());

    if let Err(e) = bar::create_bars(app, &bar_label, &bar_config) {
      print_setup_error(&format!("Failed to create bars for bar config '{}': {:#?}", bar_label, e), false);
      std::process::exit(1);
    }
  }

  app.tray_handle().get_item(TRAY_HIDE_ALL).set_enabled(true)?;

  Ok(())
}

fn get_config_from_state(config: &State<Config>, bar_label: &str) -> BarConfig {
  let locked_config = config.0.lock().unwrap();
  locked_config.bars.get(bar_label).unwrap().clone()
}

fn get_configured_widgets_from_state(config: &State<Config>) -> HashMap<String, ConfiguredWidget> {
  let locked_config = config.0.lock().unwrap();
  locked_config.widgets.as_ref().unwrap().clone()
}

#[tauri::command]
pub fn retrieve_config(bar_label: String, bar_window: tauri::Window, config_state: State<Config>) -> BarConfig {
  let bar_config = get_config_from_state(&config_state, &bar_label.as_str());
  
  if bar_config.win_app_bar.unwrap_or(false) {
    super::bar::register_win32_app_bar(bar_window, &bar_label, &bar_config);
  }
  
  bar_config
}

#[tauri::command]
pub fn retrieve_styles() -> String {
  // TODO https://docs.rs/rsass/latest/rsass/
  "body {background: blue}".to_string()
}

#[tauri::command]
pub fn retrieve_widgets(bar_label: String, config_state: State<Config>) -> HashMap<String, Vec<BarWidget>> {
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
