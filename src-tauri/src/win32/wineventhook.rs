use std::sync::Once;

use tauri::AppHandle;
use tokio::sync::mpsc;
use windows::Win32::Foundation::HWND;
use wineventhook::{
    raw_event::{OBJECT_NAMECHANGE, SYSTEM_CAPTUREEND, SYSTEM_FOREGROUND, SYSTEM_MOVESIZEEND},
    AccessibleObjectId, EventFilter, WindowEvent, WindowEventHook,
};

use crate::widgets;

static INIT_WIN_EVENT_LISTENER: Once = Once::new();

pub async fn win_event_lister(app_handle: AppHandle) -> Result<(), std::io::Error> {
    let (tx, mut rx) = mpsc::unbounded_channel();

    let event_filter = EventFilter::default();
    let _ = event_filter.skip_own_process(true);
    let hook = WindowEventHook::hook(event_filter, tx).await.unwrap();

    while let Some(event) = rx.recv().await {
        handle_win_event(event, &app_handle);
    }

    hook.unhook().await
}

fn handle_win_event(event: WindowEvent, app_handle: &AppHandle) {
    if event.raw.object_id != 0 {
        return;
    }

    let event_type = event.raw.event_id as i32;
    let hwnd = HWND(event.raw.window_handle as isize);

    if event.object_type() == AccessibleObjectId::Window {
        match event_type {
            SYSTEM_FOREGROUND | OBJECT_NAMECHANGE => {
                widgets::active_window::handle_window_title_change(app_handle, hwnd)
            }
            _ => {}
        };
    };
}

#[tauri::command]
pub fn init_win_event_hook(app_handle: tauri::AppHandle) {
    INIT_WIN_EVENT_LISTENER.call_once(move || {
        log::info!("Initialisng WinEventHook listener.");
        tauri::async_runtime::spawn(async move {
            win_event_lister(app_handle).await.unwrap();
        });
    });
}
