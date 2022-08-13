use crate::core::configuration::BarEdge;
use crate::utils;
use anyhow::Result;
use std::collections::HashMap;
use std::mem;
use tauri::Window;
use windows::Win32::Foundation::{HWND, RECT};
use windows::Win32::UI::Shell::{
    SHAppBarMessage, ABE_BOTTOM, ABE_LEFT, ABE_RIGHT, ABE_TOP, APPBARDATA,
};
use windows::Win32::UI::WindowsAndMessaging::WM_USER;

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

pub fn abd_create(hwnd: HWND, edge: Option<BarEdge>) -> Result<APPBARDATA> {
    let mut abd = APPBARDATA::default();
    abd.cbSize = mem::size_of::<APPBARDATA>() as u32;
    abd.hWnd = hwnd;
    abd.uCallbackMessage = WM_USER + 0x01;

    if edge.is_some() {
        abd.uEdge = edge_to_abe(edge.unwrap());
    }

    return Ok(abd);
}

pub fn ab_register_and_position(
    window: tauri::Window,
    edge: BarEdge,
    thickness: u32,
) -> Result<()> {
    let mut abd = abd_create(window.hwnd()?.clone(), Some(edge.clone()))?;
    abm_new(&mut abd);

    let monitor_rect = utils::get_monitor_from_window(abd.hWnd.clone());
    let monitor_width = monitor_rect.right - monitor_rect.left;
    let monitor_height = monitor_rect.bottom - monitor_rect.top;

    abd.rc = RECT::default();

    if (abd.uEdge == ABE_LEFT) || (abd.uEdge == ABE_RIGHT) {
        abd.rc.top = monitor_rect.top;
        abd.rc.bottom = monitor_rect.top + monitor_height;

        if abd.uEdge == ABE_LEFT {
            abd.rc.left = monitor_rect.left;
            abd.rc.right = abd.rc.left + thickness as i32;
        } else {
            abd.rc.left = monitor_rect.right - thickness as i32;
            abd.rc.right = monitor_rect.right;
        }
    } else {
        abd.rc.left = monitor_rect.left;
        abd.rc.right = monitor_rect.left + monitor_width;

        if abd.uEdge == ABE_TOP {
            abd.rc.top = monitor_rect.top;
            abd.rc.bottom = monitor_rect.top + thickness as i32;
        } else {
            abd.rc.top = monitor_rect.bottom - thickness as i32;
            abd.rc.bottom = monitor_rect.bottom;
        }
    }

    abm_set_pos(&mut abd);

    return Ok(());
}

pub fn ab_remove(window: &tauri::Window) -> Result<()> {
    let mut abd = abd_create(window.hwnd()?, None)?;
    abm_remove(&mut abd);
    Ok(())
}

pub fn ab_remove_all(window_list: &HashMap<String, Window>) -> Result<()> {
    for (_, window) in window_list {
        ab_remove(&window)?;
    }
    Ok(())
}

pub fn edge_to_abe(edge: BarEdge) -> u32 {
    match edge {
        BarEdge::Top => ABE_TOP,
        BarEdge::Left => ABE_LEFT,
        BarEdge::Bottom => ABE_BOTTOM,
        BarEdge::Right => ABE_RIGHT,
    }
}
