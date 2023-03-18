use tauri::{AppHandle, Manager};
use windows::Win32::Foundation::{HWND, POINT, RECT};
use windows::Win32::Graphics::Gdi::{GetMonitorInfoW, MonitorFromWindow, HMONITOR, MONITORINFO, MONITOR_DEFAULTTONEAREST};
use windows::Win32::UI::Shell::{
    SHQueryUserNotificationState, QUNS_BUSY, QUNS_PRESENTATION_MODE, QUNS_RUNNING_D3D_FULL_SCREEN,
};
use windows::Win32::UI::WindowsAndMessaging::{GetClassNameW, GetWindowRect, WindowFromPoint};

use crate::core::constants::IGNORED_FULLSCREEN_CLASSES;
use crate::core::events::BarEvent;

pub fn is_fullscreen_present() -> bool {
    let user_notification_state = unsafe { SHQueryUserNotificationState() }.unwrap();

    match user_notification_state {
        QUNS_BUSY | QUNS_RUNNING_D3D_FULL_SCREEN | QUNS_PRESENTATION_MODE => true,
        _ => false,
    }
}

pub unsafe fn is_monitor_fullscreen(window_handle: HWND) -> bool {
    let mut class_name_buf: [u16; 32] = [0u16; 32];
    let mut monitor_info = MONITORINFO::default();
    let mut top_window_rect = RECT::default();
    monitor_info.cbSize = std::mem::size_of::<MONITORINFO>() as u32;

    let hwmon: HMONITOR = MonitorFromWindow(window_handle, MONITOR_DEFAULTTONEAREST);
    GetMonitorInfoW(hwmon, &mut monitor_info);

    let mut monitor_center_point = POINT::default();
    monitor_center_point.x = (monitor_info.rcMonitor.right - monitor_info.rcMonitor.left) / 2;
    monitor_center_point.y = (monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top) / 2;

    let top_window_hwnd = WindowFromPoint(monitor_center_point);
    GetWindowRect(top_window_hwnd, &mut top_window_rect);
    GetClassNameW(top_window_hwnd, &mut class_name_buf);

    let class_name_raw = String::from_utf16(&mut class_name_buf).unwrap();
    let class_name = &class_name_raw.trim_matches(char::from(0));

    return !IGNORED_FULLSCREEN_CLASSES.contains(&class_name)
        && top_window_rect.left <= monitor_info.rcMonitor.left
        && top_window_rect.right >= monitor_info.rcMonitor.right
        && top_window_rect.top <= monitor_info.rcMonitor.top
        && top_window_rect.bottom >= monitor_info.rcMonitor.bottom;
}

pub fn hide_on_fullscreen(app_handle: AppHandle) -> () {
    std::thread::spawn(move || loop {
        std::thread::sleep(std::time::Duration::from_millis(500));

        for (label, window) in app_handle.windows() {
            let is_visible = window.is_visible().unwrap_or(true);

            if !is_fullscreen_present() || window.hwnd().is_err() || window.current_monitor().is_err() {
                if !is_visible {
                    app_handle
                        .emit_to(label.as_str(), BarEvent::ShowWindowEvent.to_string().as_str(), true)
                        .unwrap();
                }
                continue;
            }

            unsafe {
                if is_monitor_fullscreen(HWND(window.hwnd().unwrap().0.clone())) {
                    if is_visible {
                        app_handle
                            .emit_to(label.as_str(), BarEvent::HideWindowEvent.to_string().as_str(), true)
                            .unwrap();
                    }
                } else {
                    if !is_visible {
                        app_handle
                            .emit_to(label.as_str(), BarEvent::ShowWindowEvent.to_string().as_str(), true)
                            .unwrap();
                    }
                }
            }
        }
    });
}
