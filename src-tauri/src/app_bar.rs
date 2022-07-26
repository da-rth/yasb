use windows::Win32::UI::Shell::SHAppBarMessage;
use windows::Win32::UI::Shell::APPBARDATA;
use windows::Win32::UI::Shell::ABE_TOP;
use windows::Win32::UI::Shell::ABE_BOTTOM;
use anyhow::anyhow;
use std::mem;


pub fn abm_create(
  window: &tauri::Window,
  edge: &str
) -> Result<APPBARDATA, anyhow::Error> {
  let mut app_bar_data = APPBARDATA::default();

  app_bar_data.hWnd = window.hwnd()?.clone();
  app_bar_data.uEdge = if edge == "top" { ABE_TOP } else { ABE_BOTTOM };
  app_bar_data.cbSize = mem::size_of::<APPBARDATA>() as u32;
  
  abm_new(&mut app_bar_data);
  abm_position(&mut app_bar_data, window)?;

  println!(
    "Created Win32AppBar for {:?} at {}, {}, {}, {}",
    app_bar_data.hWnd,
    app_bar_data.rc.top,
    app_bar_data.rc.left,
    app_bar_data.rc.bottom,
    app_bar_data.rc.right
  );

  Ok(app_bar_data)
}

pub fn abm_position(
  mut app_bar_data: &mut APPBARDATA,
  window: &tauri::Window
) -> Result<(), anyhow::Error> {
  let monitor = window.current_monitor()?.ok_or_else(|| anyhow!("Failed to get current monitor for {}", window.label()))?;
  let monitor_pos = monitor.position();
  let monitor_size = monitor.size();
  let win_pos = window.outer_position()?;
  let win_size = window.outer_size()?;
  
  app_bar_data.rc.left = win_pos.x;
  app_bar_data.rc.right = win_pos.x + win_size.width as i32;

  if app_bar_data.uEdge == ABE_TOP {
      app_bar_data.rc.top = monitor_pos.y;
      app_bar_data.rc.bottom = monitor_pos.y + win_size.height as i32;
  } else {
      app_bar_data.rc.top = monitor_pos.y + (monitor_size.height - win_size.height) as i32;
      app_bar_data.rc.bottom = monitor_pos.y + monitor_size.height as i32;
  }

  abm_set_position(app_bar_data);

  Ok(())
}

pub fn abm_new(app_bar_data: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_NEW, app_bar_data);
  }
}

pub fn abm_set_position(app_bar_data: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_SETPOS, app_bar_data);
  }
}

pub fn abm_remove(app_bar_data: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_REMOVE, app_bar_data);
  }
}
