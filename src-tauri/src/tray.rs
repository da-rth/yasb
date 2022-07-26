
use tauri::{
    AppHandle,
    CustomMenuItem,
    SystemTray,
    SystemTrayEvent,
    SystemTrayMenu,
    SystemTrayMenuItem, Manager
};

pub fn build_tray() -> SystemTray {
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let hide = CustomMenuItem::new("hide_all".to_string(), "Hide All");
    let tray_menu = SystemTrayMenu::new()
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    SystemTray::new().with_menu(tray_menu)
}

pub fn tray_event_handler(app: &AppHandle, event: SystemTrayEvent) -> () {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            let windows = app.windows();

            match id.as_str() {
            "quit" => {
                // TODO: Remove all registered Win32AppBars by hwnd...
                std::process::exit(0);
            }

            "hide_all" => {
                println!("Hiding all windows...");
                for (label, window) in windows {
                    println!("- Hiding '{}'", label);
                    window.hide().unwrap();
                }
            }
            _ => {}
            }
        }
        _ => {}
    }
}