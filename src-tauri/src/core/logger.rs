use std::{fs::File, path::PathBuf};
use simplelog::{
  CombinedLogger,
  TermLogger,
  WriteLogger,
  Config,
  LevelFilter, TerminalMode, ColorChoice
};

use crate::core::constants::APP_LOG_FILENAME;

pub fn init_logger(verbose: bool) -> PathBuf {
  let exe_path = std::env::current_exe().expect("Failed to get current exe path");

  let mut log_path = exe_path.clone();
  log_path.pop();
  log_path.push(APP_LOG_FILENAME);

  CombinedLogger::init(
    vec![
      TermLogger::new(
        LevelFilter::Info,
        Config::default(),
        TerminalMode::Mixed,
        if verbose { ColorChoice::Never } else { ColorChoice::Auto }
      ),
      WriteLogger::new(
        LevelFilter::Info,
        Config::default(),
        File::create(log_path.clone()).unwrap()
      )
    ]
  ).expect("Failed to initialise logger");

  log_path
}