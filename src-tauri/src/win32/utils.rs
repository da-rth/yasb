use tauri::{AppHandle, Manager};
use windows::Win32::Foundation::{HWND, RECT, POINT};
use windows::Win32::Graphics::Gdi::{
  GetMonitorInfoW,
  HMONITOR,
  MONITORINFO,
  MONITOR_DEFAULTTONEAREST,
  MonitorFromWindow
};
use windows::Win32::System::Console::{AttachConsole, ATTACH_PARENT_PROCESS};
use windows::Win32::UI::HiDpi::{
  SetProcessDpiAwarenessContext,
  DPI_AWARENESS_CONTEXT_SYSTEM_AWARE
};
use windows::Win32::UI::WindowsAndMessaging::{GetWindowRect, WindowFromPoint};
use windows::core::{Result as WindowsCrateResult};
use anyhow::Result;


trait ProcessWindowsCrateResult<T> {
  fn process(self) -> Result<T>;
}

impl<T> ProcessWindowsCrateResult<T> for WindowsCrateResult<T> {
  fn process(self) -> Result<T> {
    match self {
      Ok(value) => Ok(value),
      Err(error) => Err(error.into()),
    }
  }
}

pub fn init_dpi_awareness_context() -> () {
  unsafe { SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_SYSTEM_AWARE) }
    .ok()
    .process()
    .map_err(|err| {
      eprintln!("Error setting DPI awareness context: {:?}", err)
    })
    .ok();
}

pub fn get_monitor_from_window(hwnd: HWND) -> RECT {
  unsafe {
    let monitor: HMONITOR = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST);
    let mut info: MONITORINFO = MONITORINFO::default();
    info.cbSize = std::mem::size_of::<MONITORINFO>() as u32;
    GetMonitorInfoW(monitor, &mut info);
    return info.rcMonitor;
  }
}

// pub fn is_fullscreen_present(app_handle: AppHandle) -> bool {
//   let user_notification_state = unsafe { SHQueryUserNotificationState() }.unwrap();

//   match user_notification_state {
//     QUNS_BUSY | QUNS_RUNNING_D3D_FULL_SCREEN | QUNS_PRESENTATION_MODE => true,
//     _ => false
//   }
// }

pub fn is_monitor_fullscreen(window_handle: HWND) -> bool {
    let mut monitor_info = MONITORINFO::default();
    let mut top_window_rect = RECT::default();
    monitor_info.cbSize = std::mem::size_of::<MONITORINFO>() as u32;

    unsafe {
      let hwmon: HMONITOR = MonitorFromWindow(window_handle, MONITOR_DEFAULTTONEAREST);
      GetMonitorInfoW(hwmon, &mut monitor_info);

      let mut monitor_center_point = POINT::default();
      monitor_center_point.x = (monitor_info.rcMonitor.right - monitor_info.rcMonitor.left) / 2;
      monitor_center_point.y = (monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top) / 2;

      let top_window_hwnd = WindowFromPoint(monitor_center_point);
      GetWindowRect(top_window_hwnd, &mut top_window_rect);
    }

    return top_window_rect.left == monitor_info.rcMonitor.left
        && top_window_rect.right == monitor_info.rcMonitor.right
        && top_window_rect.top == monitor_info.rcMonitor.top
        && top_window_rect.bottom == monitor_info.rcMonitor.bottom;
}

pub fn watch_fullscreen(app_handle: AppHandle) -> () {
  std::thread::spawn(move || {
    loop {
      std::thread::sleep(std::time::Duration::from_millis(500));

      for (label, window) in app_handle.windows() {
        if is_monitor_fullscreen(window.hwnd().unwrap().clone()) && window.is_visible().unwrap_or(true) {
          log::info!("Fullscreen detected on {}", window.current_monitor().unwrap().unwrap().name().unwrap());
          app_handle.emit_to(label.as_str(), "FullscreenChangeEvent", true).unwrap();
        } else if !window.is_visible().unwrap_or(true) {
          app_handle.emit_to(label.as_str(), "FullscreenChangeEvent", false).unwrap();
        }
      }
    }
  });
}

pub fn attach_console() -> () {
  unsafe { AttachConsole(ATTACH_PARENT_PROCESS); }
  std::thread::sleep(std::time::Duration::from_millis(250));
}