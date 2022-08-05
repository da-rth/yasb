use windows::Win32::Foundation::{HWND, RECT};
use windows::Win32::Graphics::Gdi::{
  GetMonitorInfoW,
  HMONITOR,
  MONITORINFO,
  MONITOR_DEFAULTTONEAREST,
  MonitorFromWindow
};
use windows::Win32::UI::HiDpi::{
  SetProcessDpiAwarenessContext,
  DPI_AWARENESS_CONTEXT_SYSTEM_AWARE};
use windows::core::Result as WindowsCrateResult;
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

pub fn setup_dpi_awareness_context() -> () {
  unsafe { SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_SYSTEM_AWARE) }
    .ok()
    .process()
    .map_err(|err| log::error!("Failed to setup DPI awareness context: {:?}", err))
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