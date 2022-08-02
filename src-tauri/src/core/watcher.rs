use std::{path::PathBuf};
use anyhow::{Result, Error};
use tauri::{AppHandle, Manager};
use notify::DebouncedEvent;
use hotwatch::Hotwatch;
use super::{configuration::{self}, constants::Event};


pub fn spawn_watchers(app_handle: &AppHandle, config_path: &PathBuf, styles_path: &PathBuf) -> Result<Hotwatch, Error> {
  let mut hotwatch = Hotwatch::new()?;

  let _closure = {
    let app_handle = app_handle.clone();

    hotwatch.watch(config_path.clone(), move |event| match event {
      DebouncedEvent::NoticeWrite(path)  | DebouncedEvent::NoticeRemove(path) => {
        let event_type = &Event::ConfigChangedEvent.to_string();
        let config = configuration::get_config(path.clone());

        println!("[Watcher] config updated: {}", path.display());
  
        match app_handle.emit_all(event_type, config) {
          Ok(_) => println!("[Watcher] Emitted {} to all bars.", event_type),
          Err(e) => eprintln!("Failed to emit {}: {}", event_type, e)
        }
      },
      _ => {}
    })?;
  };

  let _closure = {
    let app_handle = app_handle.clone();

    hotwatch.watch(styles_path.clone(), move |event| match event {
      DebouncedEvent::NoticeWrite(path) | DebouncedEvent::NoticeRemove(path) => {
        let event_type = &Event::StylesChangedEvent.to_string();
        let styles = configuration::get_styles(path.clone());

        println!("[Watcher] styles updated: {}", path.display());

        match app_handle.emit_all(event_type, styles) {
          Ok(_) => println!("[Watcher] Emitted {} to all bars.", event_type),
          Err(e) => eprintln!("Failed to emit {}: {}", event_type, e)
        }
      }
      _ => {}
    })?;
  };
    
  Ok(hotwatch)
}
