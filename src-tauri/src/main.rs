#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod core;
mod win32;
mod widgets;

use std::fs::File;

use simplelog::{
  CombinedLogger,
  TermLogger,
  WriteLogger,
  Config,
  LevelFilter, TerminalMode, ColorChoice
};

use crate::win32::utils;
use crate::core::constants::{APPLICATION_NAME, APPLICATION_LOG_FILENAME};
use crate::core::setup;
use crate::core::tray;

fn main() {
  
  CombinedLogger::init(
    vec![
        TermLogger::new(LevelFilter::Info, Config::default(), TerminalMode::Mixed, ColorChoice::Auto),
        WriteLogger::new(LevelFilter::Info, Config::default(), File::create(APPLICATION_LOG_FILENAME).unwrap())
    ]
  ).expect("Failed to initialise logger");

  utils::setup_dpi_awareness_context();

  let app_tray = tray::build_tray();
  let app_builder = tauri::Builder::default()
    .system_tray(app_tray)
    .on_system_tray_event(core::tray::tray_event_handler)
    .setup(setup::init);
  
  let app = app_builder
    .invoke_handler(tauri::generate_handler![
      setup::retrieve_widgets,
      setup::retrieve_config,
      setup::retrieve_styles
    ])
    .build(tauri::generate_context!())
    .expect(format!("Error while running {}", APPLICATION_NAME).as_str());

  // Prevent exit when all windows are closed. Exit via SysTray or termianted process
  app.run(|_app_handle, event| match event {
    tauri::RunEvent::ExitRequested { api, .. } => {
      api.prevent_exit();
    }
    _ => {}
  });
    
}
