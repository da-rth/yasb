use anyhow::{Result, Context};
use tauri::{Manager, AppHandle, PhysicalPosition, PhysicalSize};
use uuid::Uuid;
use window_vibrancy::{apply_blur, apply_acrylic, apply_mica};
use super::configuration::{BlurEffect, BarConfig, YasbConfig, validate_bar_label};
use super::constants::{FRONTEND_INDEX, FRONTEND_SETUP};
use super::tray::{TRAY_HIDE_ALL, TRAY_SHOW_ALL};
use crate::core::configuration::BarEdge;
use crate::core::constants::{DEFAULT_BAR_EDGE, DEFAULT_BAR_THICKNESS};
use crate::win32::{app_bar, self};

pub fn create_bars_from_config(app_handle: &AppHandle, config: YasbConfig) -> () {
  app_handle.tray_handle().get_item(TRAY_HIDE_ALL).set_enabled(false).expect("Failed to disable tray 'hide all' menu item");
  app_handle.tray_handle().get_item(TRAY_SHOW_ALL).set_enabled(false).expect("Failed to disable tray 'show all' menu item");

  // Close any existing windows
  for (_, window) in app_handle.windows() {
    let _ = app_bar::ab_remove(&window);
    let _ = window.close();
  }

  for (mut label, config) in config.clone().bars {
    label = validate_bar_label(&label.as_str());

    if let Err(e) = create_bars(app_handle, &label, &config) {
      log::error!("Failed to create bar(s) for bar config '{}': {:#?}", label, e);
      app_handle.exit(1);
    }
  }

  app_handle.tray_handle()
    .get_item(TRAY_HIDE_ALL)
    .set_enabled(true)
    .expect("Failed to enable tray 'hide all' menu item");
}

fn create_window(app_handle: &AppHandle, label: String, url: &str) -> Result<tauri::Window> {
  let window_builder = tauri::WindowBuilder::new(
    app_handle,
    label.clone(),
    tauri::WindowUrl::App(url.into())
  ).min_inner_size(10.0, 10.0).visible(false).transparent(true);

  window_builder.build().context(format!("Failed to build window for bar '{}'", label))
}

fn create_bar(app_handle: &AppHandle, monitor: &tauri::Monitor, bar_label: &String, bar_config: &BarConfig) -> Result<tauri::Window> {
  let uuid = Uuid::new_v4().as_simple().to_string();
  let label = format!("{}_{}", bar_label, &uuid[0..16]);
  let bar_thickness = bar_config.thickness.unwrap_or(DEFAULT_BAR_THICKNESS);
  let bar_edge = bar_config.edge.clone().unwrap_or(DEFAULT_BAR_EDGE);
  let window = create_window(app_handle, label.clone(), FRONTEND_INDEX)?;
  
  if bar_config.win_app_bar.unwrap_or(false) {
    if let Err(e) = win32::app_bar::ab_register_and_position(window.clone(), bar_edge.clone(), bar_thickness.clone()) {
      log::error!("Failed to create Win32 App Bar for {}: {}", label.clone(), e);
    }
  }

  let monitor_name = monitor.name().context(format!("Monitor for bar '{}' has NO NAME.", label));
  
  if let Some(blur_effect) = &bar_config.blur_effect {
    match blur_effect {
      BlurEffect::Blur => {
        if let Err(e) = apply_blur(&window, None) {
          log::error!("Failed to apply window effect 'acrylic' on '{}': Acrylic is only supported on Windows 10 or above. {}", label, e);
        }
      }
      BlurEffect::Acrylic => {
        if let Err(e) = apply_acrylic(&window, None) {
          log::error!("Failed to apply window effect 'acrylic' on '{}': Acrylic is only supported on Windows 10 or above. {}", label, e)
        }
      },
      BlurEffect::Mica => {
        if let Err(e) = apply_mica(&window) {
          log::error!("Failed to apply window effect 'mica' on '{}': Mica is only supported on Windows 11. {}", label, e)
        }
      }
    }
  }

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

  window.set_decorations(false)?;
  window.set_size(bar_size)?;
  window.set_skip_taskbar(true)?;
  window.set_resizable(false)?;

  win32::utils::mark_window_as_popup(window.hwnd().unwrap().clone());
  window.set_position(bar_position)?;

  log::info!(
    "Created {} on {} at {},{}",
    label,
    monitor_name?,
    bar_position.x,
    bar_position.y
  );
  Ok(window)
}

fn create_bars(app_handle: &AppHandle, bar_label: &String, bar_config: &BarConfig) -> Result<Vec<tauri::Window>> {
  let mut bars: Vec<tauri::Window> = Vec::new();
  let setup_window = create_window(app_handle, "setup_window".to_string(), FRONTEND_SETUP)?;

  for monitor in setup_window.available_monitors()? {
    if let Some(ref screen_names) = bar_config.screens.clone() {
      if screen_names.is_empty() {
        bars.push(create_bar(app_handle, &monitor, &bar_label, &bar_config)?);
      } else {
        for screen_name in screen_names {
          if screen_name == monitor.name().unwrap_or(&"".to_string()) {
            bars.push(create_bar(app_handle, &monitor, &bar_label, &bar_config)?);
          }
        }
      }
    } else {
      bars.push(create_bar(app_handle, &monitor, &bar_label, &bar_config)?);
    }
  }

  setup_window.close()?;

  Ok(bars)
}
