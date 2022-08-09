use std::ffi::{OsStr, c_void};
use std::os::windows::ffi::OsStrExt;
use tauri::{AppHandle, Manager};
use windows::Win32::Foundation::{HWND, WPARAM, LPARAM, LRESULT, HINSTANCE};
use windows::Win32::Graphics::Gdi::HBRUSH;
use windows::Win32::UI::WindowsAndMessaging::{MSG, PeekMessageA, TranslateMessage, DispatchMessageA, WM_QUIT, PM_REMOVE, CreateWindowExW, RegisterClassW, WNDCLASSW, DefWindowProcW, PostQuitMessage, WM_DESTROY, HICON, HMENU, HCURSOR, WS_OVERLAPPED, WS_MINIMIZEBOX, WS_SYSMENU, WM_DISPLAYCHANGE};
use windows::core::PCWSTR;

// WinProc listener based off @jendrikillner's implementation
// https://github.com/jendrikillner/RustMatch3/blob/master/os_window/src/os_window_lib.rs

static mut APP_HANDLE: Option<AppHandle> = None;

unsafe extern "system" fn window_proc(
    h_wnd: HWND,
    msg: u32,
    w_param: WPARAM,
    l_param: LPARAM,
) -> LRESULT {
  match msg {
    WM_DISPLAYCHANGE => {
      log::info!("WinProc: DIsplay change detected. Emitting 'ResolutionChangeEvent'");
      let _ = APP_HANDLE.clone().unwrap().emit_all("ResolutionChangeEvent", true);
    },
    WM_DESTROY => {
      PostQuitMessage(0);
    },
    _ => {}
  }

  DefWindowProcW(h_wnd, msg, w_param, l_param)
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
            std::ptr::null_mut() as *mut c_void,
          );

          let mut msg: MSG = std::mem::zeroed();

          // process messages
          loop {
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