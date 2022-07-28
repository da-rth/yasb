use super::{config::YasbConfig, tray::TRAY_HIDE_ALL};
use super::bar;
use super::config;

fn print_setup_error(msg: &str, please_fix: bool) -> () {
  let please_fix_msg = "\n\nPlease fix and try again.";
  println!("[Error] {}{}", msg, if please_fix {please_fix_msg} else {""});
}

pub fn init(app: &mut tauri::App) ->  Result<(), Box<dyn std::error::Error>> {
  let config_path = config::get_config_path();
  let config_path_str = std::fs::canonicalize(&config_path);

  let config: YasbConfig = match serde_yaml::from_str(&std::fs::read_to_string(config_path.clone())?) {
    Ok(cfg) => {
      println!("[Setup] Found configuration: {}", config_path_str?.display());
      cfg
    },
    Err(ref e) => {
      print_setup_error(&format!("Failed to load {}:\n\n{}", config_path_str?.display(), e), true);
      std::process::exit(1);
    },
  };

  for bar_config in config.bars {
    config::validate_bar_label(&bar_config.label);

    let bar_label = bar_config.label.clone();
    let bar_windows = match bar::create_bars(app, &bar_config) {
      Ok(created_bars) => created_bars,
      Err(e) => {
        print_setup_error(&format!("Failed to create bars for bar config '{}': {:#?}", bar_label, e), false);
        std::process::exit(1);
      }
    };

    if bar_config.win_app_bar.unwrap_or(false) {
      for bar_window in bar_windows {
        bar::register_win32_app_bar(bar_window, &bar_config);
      }
    }
  }

  app.tray_handle().get_item(TRAY_HIDE_ALL).set_enabled(true)?;

  Ok(())
}