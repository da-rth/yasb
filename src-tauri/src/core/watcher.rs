use std::{path::PathBuf};
use anyhow::{Result, Error};
use serde::Serialize;
use tauri::State;
use tauri::{AppHandle, Manager};
use notify::DebouncedEvent;
use hotwatch::Hotwatch;
use tauri::api::notification::Notification;
use crate::core::bar;
use crate::core::configuration;
use crate::core::constants::{
  Event,
  APPLICATION_IDENTIFIER,
  APPLICATION_LOG_FILENAME,
  STYLES_FILENAME
};

use super::constants::CONFIG_FILENAME;

// TODO replace error notifications with popup dialog?
// TODO add linting or validation to scss stylesheets?

fn send_event_payload<S: Serialize + Clone>(app_handle: &AppHandle, event: Event, payload: S) -> () {
  let event_str = &event.to_string();

  match app_handle.emit_all(event_str, payload) {
    Ok(_) => {
      log::info!("Watcher - emitted event '{}' to bar(s).", event_str);
    },
    Err(e) => {
      log::error!("Watcher - failed to emit event '{}': {}", event_str, e);
    }
  }
}

fn notify_update_failure(path: String, error: Error) -> () {
  let msg = format!("Failed to update bars due to error. Please check {} for details.", APPLICATION_LOG_FILENAME);
  
  if let Err(e) = Notification::new(APPLICATION_IDENTIFIER).body(msg).show() {
    log::error!("Watcher - failed to show update failure notification for {}: {}", path.clone(), e);
  }

  log::error!("Watcher - failed to load file '{}': {}", path, error);
}

fn notify_update_success(path: String, filename: &str) -> () {
  let title = format!("Successfully updated bar(s) with {}", filename);

  if let Err(e) = Notification::new(APPLICATION_IDENTIFIER).title(title).body(path.clone()).show() {
      log::error!("Watcher - failed to show update success notification for {}: {}", path, e);
  }
}

fn handle_config_changed(event: DebouncedEvent, app_handle: AppHandle) -> () {
  match event {
    DebouncedEvent::Write(path)  | DebouncedEvent::Remove(path) => {
      let path_str = path.clone().display().to_string().replace("\\\\?\\", "");

      match configuration::get_config(&path) {
        Ok(cfg) => {
          let config_state: State<configuration::Config> = app_handle.state();
          *config_state.0.lock().unwrap() = cfg.clone();

          bar::create_bars_from_config(&app_handle, cfg);

          notify_update_success(path_str, CONFIG_FILENAME);
        },
        Err(e) => notify_update_failure(path_str, e)
      }
    },
    _ => {}
  }
}

fn handle_styles_changed(event: DebouncedEvent, app_handle: AppHandle) -> () {
  match event {
    DebouncedEvent::Write(path)  | DebouncedEvent::Remove(path) => {
      let path_str = path.clone().display().to_string().replace("\\\\?\\", "");

      match configuration::get_styles(&path) {
        Ok(css) => {
          let styles_state: State<configuration::Styles> = app_handle.state();
          *styles_state.0.lock().unwrap() = css.clone();

          send_event_payload(&app_handle, Event::StylesChangedEvent, css);
          notify_update_success(path_str, STYLES_FILENAME);
        },
        Err(e) => notify_update_failure(path_str, e)
      }
    },
    _ => {}
  }
}

pub fn spawn_watchers(app_handle: AppHandle, config_path: PathBuf, styles_path: PathBuf) -> Result<Hotwatch, Error> {
  let mut hotwatch = Hotwatch::new()?;

  let _closure = {
    let app_handle = app_handle.clone();
    hotwatch.watch(config_path.clone(), move |event| {
      handle_config_changed(event, app_handle.clone())
    })?;
  };

  let _closure = {
    let app_handle = app_handle.clone();
    hotwatch.watch(styles_path.clone(), move |event| {
      handle_styles_changed(event, app_handle.clone())
    })?;
  };
    
  Ok(hotwatch)
}
