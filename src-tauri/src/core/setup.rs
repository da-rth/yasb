use crate::core::constants::{CONFIG_FILENAME, STYLES_FILENAME};
use crate::core::{bar, cli, configuration, logger, watcher};
use crate::widgets::sys_info::SysInfoSystemState;
// use crate::widgets::sys_info::CpuLoadState;
use crate::win32;
use std::fs::canonicalize;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use sysinfo::{System, SystemExt};
use tauri::{AppHandle, Manager};

use super::configuration::YasbConfig;

pub fn init(app: &mut tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let app_handle = app.app_handle().clone();
    let app_name = app.config().package.product_name.clone().unwrap();
    let app_version = app.config().package.version.clone().unwrap();
    let config_path;
    let styles_path;

    let (arg_verbose, arg_config_path, arg_styles_path) = cli::parse_cmd_args(app);

    let log_path = logger::init_logger(arg_verbose);

    log::info!("Initialising {} v{}", app_name, app_version);
    log::info!(
        "Logging to: {}",
        canonicalize(log_path)?.display().to_string().replace("\\\\?\\", "")
    );

    config_path = if arg_config_path.is_some() && arg_config_path.clone().unwrap().exists() {
        arg_config_path.unwrap()
    } else {
        if arg_config_path.is_some() {
            log::warn!(
                "Configuration at path '{}' does not exist. Ignoring.",
                arg_config_path.unwrap().display()
            );
        }
        configuration::get_configuration_file(CONFIG_FILENAME)
    };

    styles_path = if arg_styles_path.is_some() && arg_styles_path.clone().unwrap().exists() {
        arg_styles_path.unwrap()
    } else {
        if arg_styles_path.is_some() {
            log::warn!(
                "Stylesheet at path '{}' does not exist. Ignoring.",
                arg_styles_path.unwrap().display()
            );
        }
        configuration::get_configuration_file(STYLES_FILENAME)
    };

    log::info!(
        "Found config at: {}",
        canonicalize(config_path.clone())?
            .display()
            .to_string()
            .replace("\\\\?\\", "")
    );
    log::info!(
        "Found stylesheet at: {}",
        canonicalize(styles_path.clone())?
            .display()
            .to_string()
            .replace("\\\\?\\", "")
    );

    init_ctrlc_handler(app_handle.clone());

    let (config, styles) = init_config_paths(&app_handle, &config_path, &styles_path);
    app_handle.manage(configuration::Config(Arc::new(Mutex::new(config.clone()))));
    app_handle.manage(configuration::Styles(Arc::new(Mutex::new(styles.clone()))));
    app_handle.manage(SysInfoSystemState(Arc::new(Mutex::new(System::new_all()))));

    // Create the bars based on given config. Styles are set later...
    bar::create_bars_from_config(&app_handle, config.clone());

    log::info!("Initialising background listeners.");
    init_background_listeners(app_handle.clone(), config_path.clone(), styles_path.clone(), config.clone());

    log::info!("Initialisation complete.");
    Ok(())
}

fn init_background_listeners(app_handle: AppHandle, config_path: PathBuf, styles_path: PathBuf, config: YasbConfig) -> () {
    // If any bar(s) have always_on_top enabled, watch and hide whenever fullscreen is active
    if config.bars.into_iter().any(|(_, bar_config)| bar_config.always_on_top) {
        log::info!("Always on top detected. Window(s) will be automatically hidden when fullscreen is detected.");
        win32::fullscreen::hide_on_fullscreen(app_handle.clone());
    }

    win32::winproc::listen(app_handle.clone());

    let hotwatch = watcher::spawn_watchers(app_handle.clone(), config_path.clone(), styles_path.clone())
        .expect("File watcher failed to initialise!");

    std::mem::forget(hotwatch);
}

fn init_ctrlc_handler(app_handle: AppHandle) -> () {
    ctrlc::set_handler(move || {
        log::info!("Ctrl+C detected. Cleaning up.");
        let _ = win32::app_bar::ab_remove_all(&app_handle.windows());
        log::info!(
            "Exiting {}. Goodbye :)",
            app_handle.config().package.product_name.clone().unwrap()
        );
        app_handle.exit(0);
    })
    .expect("Error setting Ctrl-C handler")
}

fn init_config_paths(
    app_handle: &AppHandle,
    config_path: &PathBuf,
    styles_path: &PathBuf,
) -> (configuration::YasbConfig, String) {
    let config = match configuration::get_config(&config_path) {
        Ok(cfg) => cfg,
        Err(e) => {
            log::error!("Failed to load config: {}", e);
            app_handle.exit(1);
            std::process::exit(1);
        }
    };

    let styles = match configuration::get_styles(&styles_path) {
        Ok(styles) => styles,
        Err(e) => {
            log::error!("Failed to load stylesheet: {}", e);
            app_handle.exit(1);
            std::process::exit(1);
        }
    };

    (config, styles)
}
