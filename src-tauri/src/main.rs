#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod bars;
mod windows;
mod config;
mod tray;
pub mod app_bar;

// TODO implement state for bars and their widgets
// Example: https://github.com/tauri-apps/tauri/discussions/1336#discussioncomment-1936664

fn init(app: &mut tauri::App) ->  Result<(), Box<dyn std::error::Error>> {
  let _config = config::get_config_path();
  println!("Config found at {}", std::fs::canonicalize(&_config)?.display());

  let bars = match bars::create_bars(app) {
    Ok(created_bars) => created_bars,
    Err(e) => {
      eprintln!("Error - Failed to create bars: {:#?}", e);
      std::process::exit(1)
    }
  };

  for bar_window in bars {
    bar_window.show()?;
  }

  Ok(())
}

fn main() {
  windows::setup_dpi_awareness_context();

  let app_tray = tray::build_tray();
  
  let app = tauri::Builder::default()
    .system_tray(app_tray)
    .on_system_tray_event(tray::tray_event_handler)
    .setup(init);

  app.run(tauri::generate_context!())
    .expect("error while running yasb");
}
