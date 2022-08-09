use tauri::{
    AppHandle,
    CustomMenuItem,
    SystemTray,
    SystemTrayEvent,
    SystemTrayMenu,
    SystemTrayMenuItem,
    Manager
};
use anyhow::Result;
use crate::win32;

pub const TRAY_QUIT: &str = "quit";
pub const TRAY_HIDE_ALL: &str = "hide_all";
pub const TRAY_SHOW_ALL: &str = "show_all";

#[derive(strum_macros::Display)]
enum TrayEvent {
  HideAllWindowsEvent,
  ShowAllWindowsEvent
}

pub fn build_tray() -> SystemTray {
    let quit = CustomMenuItem::new(TRAY_QUIT, "Quit");
    let mut hide = CustomMenuItem::new(TRAY_HIDE_ALL, "Hide All");
    let mut show = CustomMenuItem::new(TRAY_SHOW_ALL, "Show All");

    hide.enabled = false;
    show.enabled = false;

    let tray_menu = SystemTrayMenu::new()
        .add_item(hide)
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    SystemTray::new().with_menu(tray_menu)
}

pub fn tray_event_handler(app: &AppHandle, event: SystemTrayEvent) -> () {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            log::info!("Tray: handling click for menu item '{}'.", id.as_str());

            if let Err(error) = handle_menu_item_click(id.clone(), app) {
                log::error!("Tray: failed handling click for menu item '{}': {:?}", id.as_str(), error);
            }
        }
        _ => {}
    }
}

fn handle_menu_item_click(menu_id: String, app_handle: &AppHandle) -> Result<()> {
    let windows = app_handle.windows();
    let tray_handle = app_handle.tray_handle();
    let app_name = app_handle.config().package.product_name.clone().unwrap();

    match menu_id.as_str() {
        TRAY_QUIT => {
            log::info!("Exiting {}. Goodbye :)", app_name);
            win32::app_bar::ab_remove_all(&windows)?;
            app_handle.exit(1);
            //app_handle.restart();
        },

        TRAY_HIDE_ALL => {
            log::info!("Hiding all windows...");
            app_handle.emit_all(TrayEvent::HideAllWindowsEvent.to_string().as_str(), true)?;
            tray_handle.get_item(TRAY_HIDE_ALL).set_enabled(false)?;
            tray_handle.get_item(TRAY_SHOW_ALL).set_enabled(true)?;
        },

        TRAY_SHOW_ALL => {
            log::info!("Showing all windows...");
            app_handle.emit_all(TrayEvent::ShowAllWindowsEvent.to_string().as_str(), false)?;
            tray_handle.get_item(TRAY_SHOW_ALL).set_enabled(false)?;
            tray_handle.get_item(TRAY_HIDE_ALL).set_enabled(true)?;
        }
        _ => {}
    };

    Ok(())
}