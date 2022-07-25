#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod setup;
mod windows;

fn main() {
  windows::setup_dpi_awareness_context()
    .map_err(|err| println!("{:?}", err))
    .ok();

  tauri::Builder::default()
    .setup(|app| {
      let _bars = setup::create_bars(app);
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
