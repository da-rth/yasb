use windows::Win32::Foundation::{HWND, RECT};
use windows::Win32::UI::Shell::{
  ABE_BOTTOM,
  ABE_LEFT,
  ABE_TOP,
  ABE_RIGHT,
  APPBARDATA,
  SHAppBarMessage,
};
use windows::Win32::UI::WindowsAndMessaging::{MoveWindow, WM_USER};
use anyhow::Result;
use std::mem;
use crate::core::config::BarEdge;
use crate::core::constants::DEFAULT_BAR_EDGE;
use crate::utils;

pub fn abm_new(pabd: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_NEW, pabd);
  }
}

pub fn abm_set_pos(pabd: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_SETPOS, pabd);
  }
}

#[allow(dead_code)]
pub fn abm_remove(pabd: *mut APPBARDATA) -> () {
  unsafe {
    SHAppBarMessage(windows::Win32::UI::Shell::ABM_REMOVE, pabd);
  }
}

pub fn abd_move_win(abd: APPBARDATA) -> () {
  unsafe {
    MoveWindow(
      abd.hWnd, 
      abd.rc.left, 
      abd.rc.top, 
      abd.rc.right - abd.rc.left, 
      abd.rc.bottom - abd.rc.top, 
      true
    );
  }
}

pub fn abd_create(hwnd: HWND) -> Result<APPBARDATA> {
  let mut abd = APPBARDATA::default();
  
  abd.cbSize = mem::size_of::<APPBARDATA>() as u32;
  abd.hWnd = hwnd;
  abd.uCallbackMessage = WM_USER + 0x01; 

  return Ok(abd);
}

pub fn abd_set_pos(pabd: &mut APPBARDATA, window_rect: RECT, edge: u32) -> Result<()> {
  let monitor_rect = utils::get_monitor_from_window(pabd.hWnd);
  let monitor_width = monitor_rect.right - monitor_rect.left;
  let monitor_height = monitor_rect.bottom - monitor_rect.top;
  let window_width = window_rect.right - window_rect.left;
  let window_height = window_rect.top - window_rect.bottom;
  let mut bar_height = window_height; 
  let mut bar_width = window_width; 

  pabd.uEdge = edge;
  pabd.rc = window_rect;

  if (edge == ABE_LEFT) || (edge == ABE_RIGHT) { 
    bar_width = pabd.rc.right - pabd.rc.left;
    pabd.rc.top = monitor_rect.top;
    pabd.rc.bottom = monitor_rect.top + monitor_height;
  } else {
    bar_height = pabd.rc.bottom - pabd.rc.top;
    pabd.rc.left = monitor_rect.left;
    pabd.rc.right = monitor_rect.left + monitor_width;
  }

  match edge {
    ABE_LEFT => {
      pabd.rc.right = pabd.rc.left + bar_width;
    }
    ABE_RIGHT => {
      pabd.rc.left = pabd.rc.right - bar_width; 
    }
    ABE_TOP => {
      pabd.rc.bottom = pabd.rc.top + bar_height;
    }
    ABE_BOTTOM => {
      pabd.rc.top = pabd.rc.bottom - bar_height; 
    }
    _ => {}
  }

  return Ok(());
}

pub fn ab_register_and_position(window: &tauri::Window, bar_edge: Option<BarEdge>) -> Result<APPBARDATA> {
  let mut abd = abd_create(window.hwnd()?.clone())?;
  let mut win_rect = RECT::default();
  let win_pos = window.outer_position()?.clone();
  let win_size = window.outer_size()?.clone();
  let edge = edge_to_abe(bar_edge.unwrap_or(DEFAULT_BAR_EDGE));
  
  win_rect.top = win_pos.x;
  win_rect.left = win_pos.y;
  win_rect.bottom = win_rect.top + win_size.height as i32;
  win_rect.right = win_rect.left + win_size.width as i32;

  abm_new(&mut abd);
  abd_set_pos(&mut abd, win_rect, edge)?;
  abm_set_pos(&mut abd);
  abd_move_win(abd);

  println!(
    "[Setup] Created Win32AppBar for '{}' at {},{} {}x{}",
    &window.label(),
    abd.rc.top,
    abd.rc.left,
    win_size.width,
    win_size.height
  );

  return Ok(abd);
}

pub fn ab_remove(window: &tauri::Window) -> Result<()> {
  let mut abd = abd_create(window.hwnd()?)?;
  abm_remove(&mut abd);
  Ok(())
}

pub fn edge_to_abe(edge: BarEdge) -> u32 {
  match edge {
    BarEdge::Top => ABE_TOP,
    BarEdge::Left => ABE_LEFT,
    BarEdge::Bottom => ABE_BOTTOM,
    BarEdge::Right => ABE_RIGHT
  }
}