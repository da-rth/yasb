use crate::core::constants::{CLI_ARG_CONFIG, CLI_ARG_HELP, CLI_ARG_STYLES, CLI_ARG_VERBOSE, CLI_ARG_VERSION};
use crate::win32;
use std::path::PathBuf;
use tauri::Manager;

pub fn parse_cmd_args(app: &mut tauri::App) -> (bool, Option<PathBuf>, Option<PathBuf>) {
    let mut arg_verbose = false;
    let mut arg_styles_path: Option<PathBuf> = None;
    let mut arg_config_path: Option<PathBuf> = None;

    match app.get_cli_matches() {
        Ok(matches) => {
            for (arg, arg_data) in matches.args {
                if arg != CLI_ARG_HELP && arg != CLI_ARG_VERSION && arg_data.occurrences == 0 {
                    continue;
                }

                match arg.as_str() {
                    CLI_ARG_CONFIG => {
                        let config_path_str: String = serde_json::from_value(arg_data.value).unwrap();
                        arg_config_path = Some(PathBuf::from(config_path_str));
                    }
                    CLI_ARG_STYLES => {
                        let styles_path_str: String = serde_json::from_value(arg_data.value).unwrap();
                        arg_styles_path = Some(PathBuf::from(styles_path_str));
                    }
                    CLI_ARG_VERBOSE => {
                        win32::utils::attach_console();
                        arg_verbose = true;
                    }
                    CLI_ARG_HELP => {
                        win32::utils::attach_console();
                        let str_val: String = serde_json::from_value(arg_data.value).unwrap();
                        println!("{}", str_val);
                        app.app_handle().exit(0);
                    }
                    CLI_ARG_VERSION => {
                        win32::utils::attach_console();
                        println!("{}", app.package_info().version.to_string());
                        app.app_handle().exit(0);
                    }
                    _ => {
                        log::error!(
                            "Unknown CLI argument '{}'. Use argument `--help` to print help information.",
                            arg
                        );
                    }
                }
            }
        }
        Err(_) => {}
    }

    (arg_verbose, arg_config_path, arg_styles_path)
}
