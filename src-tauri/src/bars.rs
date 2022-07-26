use anyhow::Result;
use crate::app_bar;

const APP_INDEX: &str = "index.html";
const WIN_APP_BAR: bool = false;
const BAR_HEIGHT: u32 = 64;


fn create_window(app: &mut tauri::App, label: String) -> Result<tauri::Window, tauri::Error> {
  let mut window = tauri::WindowBuilder::new(app, label, tauri::WindowUrl::App(APP_INDEX.into()));
  window = window.visible(false);
  window.build()
}

fn create_bar(app: &mut tauri::App, bar_index: usize, monitor: &tauri::Monitor) -> Result<tauri::Window> {
  let bar_label = format!("{}{}", "bar_", bar_index+1);
  let bar_window = create_window(app, bar_label.clone())?;
  let bar_position = tauri::PhysicalPosition::new(monitor.position().x, monitor.position().y);
  let bar_size = tauri::PhysicalSize::new( monitor.size().width, BAR_HEIGHT);
  let no_name: String = "NO DISPLAY NAME".to_string();
  let monitor_name = monitor.name().unwrap_or(&no_name);
  
  print!(
    "Created Bar '{}' {:?} on {} at x: {}, y: {}\n",
    bar_label,
    bar_window.hwnd()?,
    monitor_name,
    bar_position.x,
    bar_position.y
  );
  
  bar_window.hide()?;
  bar_window.set_decorations(false)?;
  bar_window.set_size(bar_size)?;
  bar_window.set_position(bar_position)?;
  bar_window.set_skip_taskbar(true)?;

  if WIN_APP_BAR {
    app_bar::abm_create(&bar_window, "top")?;
  }

  Ok(bar_window)
}

pub fn create_bars(app: &mut tauri::App) -> Result<Vec<tauri::Window>> {
  let mut bars: Vec<tauri::Window> = Vec::new();
  let setup_window = create_window(app, "setup_window".to_string()).unwrap();
  let monitors = setup_window.available_monitors().unwrap();

  for (idx, monitor) in monitors.iter().enumerate() {
    bars.push(create_bar(app, idx, &monitor)?);
  }

  setup_window.close()?;

  Ok(bars)
}
