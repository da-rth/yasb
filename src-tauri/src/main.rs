#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod core;
mod win32;
mod widgets;

use crate::win32::utils;
use crate::core::constants::APPLICATION_NAME;
use crate::core::setup;
use crate::core::config;

fn main() {
  utils::setup_dpi_awareness_context();
  let cfg = core::config::get_config();
  let app_tray = core::tray::build_tray();
  
  let app_builder = tauri::Builder::default()
    .manage(config::Config(cfg))
    .system_tray(app_tray)
    .on_system_tray_event(core::tray::tray_event_handler)
    .setup(setup::init);
  
  app_builder
    .invoke_handler(tauri::generate_handler![
      setup::retrieve_widgets,
      setup::retrieve_config,
      setup::retrieve_styles
    ])
    .run(tauri::generate_context!())
    .expect(format!("Error while running {}", APPLICATION_NAME).as_str());
}
