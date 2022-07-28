#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod core;
mod win32;

use crate::win32::utils;
use crate::core::constants::APPLICATION_NAME;
use crate::core::setup;

fn main() {
  utils::setup_dpi_awareness_context();

  let app_tray = core::tray::build_tray();
  
  let app_builder = tauri::Builder::default()
    .system_tray(app_tray)
    .on_system_tray_event(core::tray::tray_event_handler)
    .setup(setup::init);

  app_builder.run(tauri::generate_context!())
    .expect(format!("Error while running {}", APPLICATION_NAME).as_str());
}
