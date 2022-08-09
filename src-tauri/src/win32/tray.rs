use std::ffi::c_void;

use windows::{Win32::{UI::{WindowsAndMessaging::{FindWindowW, FindWindowExW, SendMessageW, GetWindowThreadProcessId, HICON}, Controls::{TB_BUTTONCOUNT, TBBUTTONINFOW, TBIF_BYINDEX, TBIF_IMAGE, TBIF_COMMAND, TBIF_LPARAM, TBIF_STATE, TB_GETBUTTONINFOW, TBBUTTON}, Shell::{NOTIFYICONDATAW, NOTIFYICONDATAW_0}}, Foundation::{HWND, LPARAM, WPARAM, LRESULT, HANDLE}, System::{Threading::{OpenProcess, PROCESS_ALL_ACCESS}, Memory::{VirtualAllocEx, MEM_RESERVE, MEM_COMMIT, PAGE_READWRITE}, Diagnostics::Debug::{WriteProcessMemory, ReadProcessMemory}}}, core::PCWSTR};


pub unsafe fn find_tray_toolbar_window() -> Option<HWND> {
  let hwnd_tray = FindWindowW("Shell_TrayWnd", PCWSTR(std::ptr::null()));
  
  if hwnd_tray.0 != 0 {
    let hwnd_tray_notify = FindWindowExW(hwnd_tray, HWND(0), "TrayNotifyWnd", PCWSTR(std::ptr::null()));

    if hwnd_tray_notify.0 != 0 {
      let hwnd_sys_notify = FindWindowExW(hwnd_tray_notify, HWND(0), "SysPager", PCWSTR(std::ptr::null()));

      if hwnd_sys_notify.0 != 0 {
        return Some(FindWindowExW(hwnd_sys_notify, HWND(0), "ToolbarWindow32", PCWSTR(std::ptr::null())));
      }
    }
  }

  return None;
}

// Currently doesn't work, but should print information for each 
// Implementation based on
// https://social.msdn.microsoft.com/Forums/vstudio/en-US/dd2b6360-0077-4b69-8126-fb6d52b7eb20/get-all-tray-icons-in-taskbar-and-display-them-in-wpf?forum=wpf
pub unsafe fn get_tray_icons () -> () {
  let hwnd_tray_toolbar = find_tray_toolbar_window();

  if hwnd_tray_toolbar.is_none() {
    eprintln!("Cannot find SysPager/ToolbarWindow32");
    return;
  }

  let mut dw_pid: u32 = 0;
  let mut i = 0;
  let tray_num_buttons = SendMessageW(hwnd_tray_toolbar.unwrap(), TB_BUTTONCOUNT, WPARAM(0), LPARAM(0)).0;
    
  GetWindowThreadProcessId(hwnd_tray_toolbar,&mut dw_pid);

  let h_process = OpenProcess(PROCESS_ALL_ACCESS, false, dw_pid).unwrap();

  if h_process.0 == 0 {
    eprintln!("Cannot find SysPager/ToolbarWindow32");
    return;
  }

  println!("tray icons: {}", tray_num_buttons);

  while i < tray_num_buttons {
    let p_sys_tb_button_info = VirtualAllocEx(
      h_process,
      std::ptr::null_mut() as *mut c_void,
      std::mem::size_of::<TBBUTTONINFOW>(),
      MEM_RESERVE | MEM_COMMIT,
      PAGE_READWRITE
    );
    
    let mut tb_button_info = TBBUTTONINFOW::default();
    tb_button_info.cbSize = std::mem::size_of::<TBBUTTONINFOW>() as u32;
    tb_button_info.dwMask = TBIF_BYINDEX | TBIF_IMAGE | TBIF_COMMAND | TBIF_LPARAM | TBIF_STATE;

    let mut num_bytes_read: usize  = 0;

    let b_ret = WriteProcessMemory(
      h_process, 
      p_sys_tb_button_info,
      &mut tb_button_info as *mut _ as *mut c_void, 
      tb_button_info.cbSize as usize, 
      &mut num_bytes_read
    );

    if b_ret.0 != 1 {
      return;
    }

    let n_ret = SendMessageW(
      hwnd_tray_toolbar,
      TB_GETBUTTONINFOW,
      WPARAM(i as usize),
      LPARAM(p_sys_tb_button_info as isize)
    );

    if n_ret.0 == -1 {
      return;
    }

    let b_ret = ReadProcessMemory(
      h_process, 
      p_sys_tb_button_info, 
      &mut tb_button_info as *mut _ as *mut c_void, 
      tb_button_info.cbSize as usize, 
      &mut num_bytes_read
    );

    if b_ret.0 != 1 {
      return;
    }

    let mut data = NOTIFYICONDATAW::default();
    data.cbSize = std::mem::size_of::<NOTIFYICONDATAW>() as u32;

    let b_rett = ReadProcessMemory(
      h_process, 
      &tb_button_info.lParam as *const _ as *const c_void, 
      &mut data as *mut _ as *mut c_void, 
      data.cbSize.clone() as usize, 
      &mut num_bytes_read
    );

    if b_rett.0 != 0 {
      // tray data retrieved 
    }

    println!("tray item: {:?} {:?}", data.hWnd, data.szInfoTitle);

    i = i + 1;
  }
}
