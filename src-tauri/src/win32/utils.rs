use anyhow::Result;
use windows::core::{Result as WindowsCrateResult, PWSTR};
use windows::Win32::Foundation::{HANDLE, HWND, RECT};
use windows::Win32::Graphics::Gdi::{
    GetMonitorInfoW, MonitorFromWindow, HMONITOR, MONITORINFO, MONITORINFOEXW,
    MONITOR_DEFAULTTONEAREST,
};
use windows::Win32::System::Console::{AttachConsole, ATTACH_PARENT_PROCESS};
use windows::Win32::System::Threading::{
    OpenProcess, QueryFullProcessImageNameW, PROCESS_NAME_WIN32, PROCESS_QUERY_INFORMATION,
};
use windows::Win32::UI::HiDpi::{
    SetProcessDpiAwarenessContext, DPI_AWARENESS_CONTEXT_SYSTEM_AWARE,
};
use windows::Win32::UI::WindowsAndMessaging::{
    GetClassNameA, GetWindowLongW, GetWindowTextLengthW, GetWindowTextW, GetWindowThreadProcessId,
    SetWindowLongW, GWL_EXSTYLE, WINDOW_EX_STYLE, WS_EX_NOACTIVATE,
};

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
        .map_err(|err| eprintln!("Error setting DPI awareness context: {:?}", err))
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

pub fn set_no_activate(hwnd: HWND) -> () {
    unsafe {
        let window_style = WINDOW_EX_STYLE(GetWindowLongW(hwnd.clone(), GWL_EXSTYLE) as u32);

        SetWindowLongW(
            hwnd.clone(),
            GWL_EXSTYLE,
            (window_style.0 | WS_EX_NOACTIVATE.0) as i32,
        );
    }
}

pub fn attach_console() -> () {
    unsafe {
        AttachConsole(ATTACH_PARENT_PROCESS);
    }
    std::thread::sleep(std::time::Duration::from_millis(250));
}

fn get_win_text_len(hwnd: HWND) -> Option<usize> {
    let length = unsafe { GetWindowTextLengthW(hwnd) };
    if length >= 0 {
        Some(length as usize)
    } else {
        None
    }
}

pub fn get_win_title(hwnd: HWND) -> Option<String> {
    let window_title_length = get_win_text_len(hwnd);

    match window_title_length {
        Some(title_len) => {
            let mut text_buffer = vec![0u16; title_len + 1 as usize];
            let bytes_read = unsafe { GetWindowTextW(hwnd, &mut text_buffer) };

            if bytes_read > 0 {
                match String::from_utf16(&text_buffer) {
                    Ok(win_title) => Some(win_title.trim_matches(char::from(0)).to_string()),
                    Err(_) => None,
                }
            } else {
                None
            }
        }
        None => None,
    }
}

pub fn get_win_class(hwnd: HWND) -> Option<String> {
    let mut class_buffer = vec![0u8; 256];
    let bytes_read = unsafe { GetClassNameA(hwnd, &mut class_buffer) };
    if bytes_read > 0 {
        match String::from_utf8(class_buffer) {
            Ok(win_class) => Some(win_class.trim_matches(char::from(0)).to_string()),
            Err(_) => None,
        }
    } else {
        None
    }
}

pub fn get_thread_process_id(hwnd: HWND) -> (u32, u32) {
    let mut process_id: u32 = 0;
    let thread_id = unsafe { GetWindowThreadProcessId(hwnd, Some(&mut process_id)) };
    (process_id, thread_id)
}

pub fn get_pid_handle(pid: u32) -> Option<HANDLE> {
    match unsafe { OpenProcess(PROCESS_QUERY_INFORMATION, false, pid) }.process() {
        Ok(handle) => Some(handle),
        Err(_) => None,
    }
}

pub fn get_exe_path(handle: HANDLE) -> Option<String> {
    let mut len = 260_u32;
    let mut path: Vec<u16> = vec![0; len as usize];
    let text_ptr = path.as_mut_ptr();

    match unsafe {
        QueryFullProcessImageNameW(
            handle,
            PROCESS_NAME_WIN32,
            PWSTR(text_ptr),
            std::ptr::addr_of_mut!(len),
        )
    }
    .ok()
    .process()
    {
        Ok(_) => Some(String::from_utf16_lossy(&path[..len as usize])),
        Err(_) => None,
    }
}

pub fn get_exe_name_from_path(path: String) -> Option<String> {
    match path.split('\\').last() {
        Some(exe_name) => Some(exe_name.to_string()),
        None => None,
    }
}

pub fn get_monitor_info(hwnd: HWND) -> MONITORINFOEXW {
    let monitor_hwnd = unsafe { MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST) };
    let mut monitor_info = MONITORINFOEXW::default();
    monitor_info.monitorInfo.cbSize = std::mem::size_of::<MONITORINFOEXW>() as u32;
    let monitor_info_ptr: *mut MONITORINFO = &mut monitor_info as *mut _ as *mut MONITORINFO;
    unsafe {
        GetMonitorInfoW(monitor_hwnd, monitor_info_ptr);
    };
    monitor_info
}

pub fn get_monitor_name(montitor_info: MONITORINFOEXW) -> Option<String> {
    let monitor_name_buf = montitor_info.szDevice;
    match String::from_utf16(&monitor_name_buf) {
        Ok(monitor_name) => Some(monitor_name.trim_matches(char::from(0)).to_string()),
        Err(_) => None,
    }
}
