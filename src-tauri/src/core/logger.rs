use serde_repr::{Deserialize_repr, Serialize_repr};
use simplelog::{ColorChoice, CombinedLogger, Config, LevelFilter, TermLogger, TerminalMode, WriteLogger};
use std::{fs::File, path::PathBuf};

use crate::core::constants::APP_LOG_FILENAME;

use super::configuration::get_configuration_file;

#[derive(Debug, Clone, Deserialize_repr, Serialize_repr)]
#[repr(u16)]
pub enum WebviewLogLevel {
    Info = 1,
    Error = 2,
    Debug = 3,
    Trace = 4,
    Warn = 5,
}

impl From<WebviewLogLevel> for log::Level {
    fn from(log_level: WebviewLogLevel) -> Self {
        match log_level {
            WebviewLogLevel::Trace => log::Level::Trace,
            WebviewLogLevel::Debug => log::Level::Debug,
            WebviewLogLevel::Info => log::Level::Info,
            WebviewLogLevel::Warn => log::Level::Warn,
            WebviewLogLevel::Error => log::Level::Error,
        }
    }
}

pub fn init_logger(verbose: bool) -> PathBuf {
    let log_path = get_configuration_file(APP_LOG_FILENAME);

    CombinedLogger::init(vec![
        TermLogger::new(
            LevelFilter::Info,
            Config::default(),
            TerminalMode::Mixed,
            if verbose {
                ColorChoice::Never
            } else {
                ColorChoice::Auto
            },
        ),
        WriteLogger::new(LevelFilter::Info, Config::default(), File::create(log_path.clone()).unwrap()),
    ])
    .expect("Failed to initialise logger");

    log_path
}
