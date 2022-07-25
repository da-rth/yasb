#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

#[cfg(windows)]
extern crate winapi;

const APP_INDEX: &str = "index.html";
const BAR_HEIGHT: u32 = 64;

fn build_window(app: &mut tauri::App, label: String) -> Result<tauri::Window, tauri::Error> {
  let mut window = tauri::WindowBuilder::new(app, label, tauri::WindowUrl::App(APP_INDEX.into()));
  // window = window.visible(false);
  window.build()
}

fn setup_bar_window(app: &mut tauri::App, bar_index: usize, monitor: &tauri::Monitor, num_monitors: usize) -> tauri::Window {
  let bar_label = format!("{}{}", "bar_", bar_index+1);
  let mut width: u32 = monitor.size().width;
  let mut height: u32 = BAR_HEIGHT;

  let bar_window = build_window(app, bar_label.clone()).unwrap();
  let bar_position = tauri::PhysicalPosition::new(monitor.position().x, monitor.position().y);
  let bar_size = tauri::PhysicalSize::new(width, height);
  
  print!("Built {} on {} ({}x{} @ {}) at x: {}, y: {}\n", bar_label, monitor.name().unwrap(), bar_size.width, bar_size.height, monitor.scale_factor(), bar_position.x, bar_position.y, );
  
  bar_window.hide().unwrap();
  bar_window.set_decorations(false).unwrap();
  bar_window.set_size(bar_size).unwrap();
  bar_window.set_position(bar_position).unwrap();
  bar_window.set_skip_taskbar(true);
  bar_window.show().unwrap();
  bar_window
}

fn setup_bars(app: &mut tauri::App) -> Vec<tauri::Window> {
  let mut bars: Vec<tauri::Window> = Vec::new();
  let setup_window = build_window(app, "setup_window".to_string()).unwrap();
  setup_window.hide();
  let monitors = setup_window.available_monitors().unwrap();

  for (idx, monitor) in monitors.iter().enumerate() {
    bars.push(setup_bar_window(app, idx, &monitor, monitors.len()));
  }
  bars
}

fn main() {
  #[cfg(target_os = "windows")]
  unsafe {
    winapi::um::shellscalingapi::SetProcessDpiAwareness(1);
  }

  tauri::Builder::default()
    .setup(|app| {
      let bars = setup_bars(app);
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
