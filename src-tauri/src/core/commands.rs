use std::collections::HashMap;
use tauri::State;
use crate::core::configuration;
use crate::widgets::{BarWidget, ConfiguredWidget};


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

fn get_config_from_state(config: &State<configuration::Config>, bar_label: &str) -> configuration::BarConfig {
  let locked_config = config.0.lock().unwrap();
  locked_config.bars.get(bar_label).unwrap().clone()
}

fn get_configured_widgets_from_state(config: &State<configuration::Config>) -> HashMap<String, ConfiguredWidget> {
  let locked_config = config.0.lock().unwrap();
  locked_config.widgets.as_ref().unwrap().clone()
}