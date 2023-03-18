#![cfg_attr(all(not(debug_assertions), target_os = "windows"), windows_subsystem = "windows")]

mod core;
mod widgets;
mod win32;

use crate::core::commands;
use crate::core::setup;
use crate::core::tray;
use crate::win32::utils;
use win32::utils::init_dpi_awareness_context;

fn main() {
    init_dpi_awareness_context();

    let app_tray = tray::build_tray();
    let app_builder = tauri::Builder::default()
        .system_tray(app_tray)
        .on_system_tray_event(core::tray::tray_event_handler)
        .setup(setup::init);

    let app = app_builder
        .invoke_handler(tauri::generate_handler![
            commands::retrieve_widgets,
            commands::retrieve_config,
            commands::retrieve_styles,
            commands::webview_log,
            // Run Once background tasks
            win32::wineventhook::win32_init_event_hook,
            widgets::komorebi::listener::komorebi_init_event_listener,
            // Widget Commands
            widgets::custom::process_custom_command,
            widgets::active_window::detect_foreground_window,
            widgets::sys_info::get_sys_info
        ])
        .build(tauri::generate_context!())
        .expect(format!("Error while running application.").as_str());

    // Prevent exit when all windows are closed. Exit via TrayIcon or by terminating process
    app.run(|_app_handle, event| match event {
        tauri::RunEvent::ExitRequested { api, .. } => {
            log::info!("Prevented exit");
            api.prevent_exit();
        }
        _ => {}
    });
}
