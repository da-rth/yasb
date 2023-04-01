use std::ffi::{c_void, OsStr};
use std::os::windows::ffi::OsStrExt;
use tauri::{AppHandle, Manager, State};
use windows::core::PCWSTR;
use windows::Win32::Foundation::{HINSTANCE, HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::Graphics::Gdi::HBRUSH;
use windows::Win32::UI::WindowsAndMessaging::{
    CreateWindowExW, DefWindowProcW, DispatchMessageA, PeekMessageA, PostQuitMessage, RegisterClassW, TranslateMessage,
    HCURSOR, HICON, HMENU, MSG, PM_REMOVE, WM_DESTROY, WM_DISPLAYCHANGE, WM_QUIT, WNDCLASSW, WS_MINIMIZEBOX, WS_OVERLAPPED,
    WS_SYSMENU,
};

use crate::core::{bar, configuration};

// WinProc listener based off @jendrikillner's implementation
// https://github.com/jendrikillner/RustMatch3/blob/master/os_window/src/os_window_lib.rs

static mut APP_HANDLE: Option<AppHandle> = None;

unsafe extern "system" fn window_proc(hwnd: HWND, msg: u32, w_param: WPARAM, l_param: LPARAM) -> LRESULT {
    let app_handle = APP_HANDLE.clone().unwrap();
    match msg {
        WM_DISPLAYCHANGE => {
            // Allow some time for added/removed monitors to update
            std::thread::sleep(std::time::Duration::from_secs(1));
            let config_state: State<configuration::Config> = app_handle.state();
            let config = config_state.0.lock().unwrap().clone();
            log::info!("WinProc: display change detected. Reloading windows...");
            bar::create_bars_from_config(&app_handle.clone(), config);
        }
        WM_DESTROY => {
            PostQuitMessage(0);
        }
        _ => {}
    }

    DefWindowProcW(hwnd, msg, w_param, l_param)
}

pub fn listen(app_handle: AppHandle) -> () {
    std::thread::spawn(move || {
        unsafe {
            APP_HANDLE = Some(app_handle.clone());

            let mut window_class_name: Vec<u16> = OsStr::new("YasbWindowClass").encode_wide().collect();
            window_class_name.push(0);

            let window_class = WNDCLASSW {
                style: windows::Win32::UI::WindowsAndMessaging::WNDCLASS_STYLES(0),
                lpfnWndProc: Some(window_proc),
                cbClsExtra: 0,
                cbWndExtra: 0,
                hInstance: HINSTANCE(0),
                hIcon: HICON(0),
                hCursor: HCURSOR(0),
                hbrBackground: HBRUSH(16),
                lpszMenuName: PCWSTR(std::ptr::null()),
                lpszClassName: PCWSTR(window_class_name.as_ptr()),
            };

            let error_code = RegisterClassW(&window_class);

            assert!(error_code != 0, "failed to register the window class");

            let h_wnd_window = CreateWindowExW(
                windows::Win32::UI::WindowsAndMessaging::WINDOW_EX_STYLE(0),
                PCWSTR(window_class_name.as_ptr()),
                PCWSTR(window_class_name.as_ptr()),
                WS_OVERLAPPED | WS_MINIMIZEBOX | WS_SYSMENU,
                0,
                0,
                0,
                0,
                HWND(0),
                HMENU(0),
                HINSTANCE(0),
                Some(std::ptr::null_mut() as *mut c_void),
            );

            let mut msg: MSG = std::mem::zeroed();

            // process messages
            loop {
                std::thread::sleep(std::time::Duration::from_secs(5));
                if PeekMessageA(&mut msg, h_wnd_window, 0, 0, PM_REMOVE).as_bool() {
                    TranslateMessage(&msg);
                    DispatchMessageA(&msg);

                    // once the window has been closed we can exit the message loop
                    if msg.message == WM_QUIT {
                        break;
                    }
                }
            }
        }
    });
}
