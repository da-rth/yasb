use anyhow::{Result, Context};
use tauri::{PhysicalSize, PhysicalPosition};
use windows::Win32::UI::WindowsAndMessaging::{GWL_STYLE, WS_POPUP, SetWindowLongW};
use super::config::{BarConfig, BarEdge};
use super::constants::{DEFAULT_BAR_EDGE, DEFAULT_BAR_THICKNESS};
use crate::win32::app_bar;

const APP_INDEX: &str = "index.html";

fn create_window(app: &mut tauri::App, label: String) -> Result<tauri::Window> {
  let window_builder = tauri::WindowBuilder::new(
    app,
    label.clone(),
    tauri::WindowUrl::App(APP_INDEX.into())
  ).min_inner_size(10.0, 10.0).visible(false).transparent(true);

  window_builder.build().context(format!("Failed to build window for bar '{}'", label))
}

fn create_bar(app: &mut tauri::App, bar_index: usize, monitor: &tauri::Monitor, bar_label: &String, bar_config: &BarConfig) -> Result<tauri::Window> {
  let label = format!("{}_{}", bar_label, bar_index+1);
  let window = create_window(app, label.clone())?;
  let bar_thickness = bar_config.thickness.unwrap_or(DEFAULT_BAR_THICKNESS);
  let bar_edge = bar_config.edge.clone().unwrap_or(DEFAULT_BAR_EDGE);

  // Default bar size and position is for top edge
  let mut bar_position = PhysicalPosition::new(monitor.position().x, monitor.position().y);
  let mut bar_size = PhysicalSize::new(monitor.size().width, bar_thickness);

  // Change bar size and position based on edge provided in bar_config
  match bar_edge {
    BarEdge::Bottom => {
      bar_position.y = monitor.position().y + monitor.size().height as i32 - bar_thickness as i32;
    },
    BarEdge::Left => {
      bar_size.width = bar_thickness;
      bar_size.height = monitor.size().height;
    },
    BarEdge::Right => {
      bar_position.x = monitor.position().x + monitor.size().width as i32 - bar_thickness as i32;
      bar_size.width = bar_thickness;
      bar_size.height = monitor.size().height;
    },
    _ => {}
  }
  
  let monitor_name = monitor.name().context(format!("Monitor for bar '{}' has NO NAME.", label));
  
  window.hide()?;
  window.set_decorations(false)?;
  window.set_size(bar_size)?;
  window.set_skip_taskbar(true)?;
  window.set_resizable(false)?;

  // Minimum window height fix
  let hwnd = window.hwnd().unwrap().clone();
  unsafe {
    SetWindowLongW(hwnd, 
      GWL_STYLE, 
      WS_POPUP.0 as i32
    );
  }

  // TODO set max width (or height) based on edge

  window.set_position(bar_position)?;

  window.show()?;
  window.set_always_on_top(bar_config.always_on_top.clone().unwrap_or(false))?;

  print!(
    "[Setup] Created Bar '{}' on display '{}' at {},{}\n",
    label,
    monitor_name?,
    bar_position.x,
    bar_position.y
  );

  Ok(window)
}

pub fn create_bars(app: &mut tauri::App, bar_label: &String, bar_config: &BarConfig) -> Result<Vec<tauri::Window>> {
  let mut bars: Vec<tauri::Window> = Vec::new();
  let setup_window = create_window(app, "setup_window".to_string()).unwrap();
  let monitors = setup_window.available_monitors().unwrap();

  // Create bars for screens defined in bar_config.screens
  // If no screens are provided in config, create bar on all available screens
  for (idx, monitor) in monitors.iter().enumerate() {
    if let Some(ref screen_names) = bar_config.screens.clone() {
      if screen_names.is_empty() {
        bars.push(create_bar(app, idx, &monitor, &bar_label, &bar_config)?);
      } else {
        for screen_name in screen_names {
          if screen_name == monitor.name().unwrap_or(&"".to_string()) {
            bars.push(create_bar(app, idx, &monitor, &bar_label, &bar_config)?);
          }
        }
      }
    } else {
      bars.push(create_bar(app, idx, &monitor, &bar_label, &bar_config)?);
    }
  }

  setup_window.close()?;

  Ok(bars)
}

pub fn register_win32_app_bar(bar_window: tauri::Window, bar_label: &str, bar_config: &BarConfig) -> () {
  app_bar::ab_register_and_position(&bar_window, bar_config.edge.clone()).unwrap();

  // Unregister Win32 App Bar if KeyboardInterrupt is detected
  ctrlc::set_handler(move || {
    app_bar::ab_remove(&bar_window).unwrap();
    let _ = bar_window.close().unwrap();
  }).expect(format!("Failed to set ctrlc handler for bar '{}'", bar_label).as_str());
}