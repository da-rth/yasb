use std::{fs::File, path::PathBuf};
use home::home_dir;
use simplelog::{
  CombinedLogger,
  TermLogger,
  WriteLogger,
  Config,
  LevelFilter, TerminalMode, ColorChoice
};

use crate::core::constants::{CONFIG_DIR_NAME, APP_LOG_FILENAME};

pub fn init_logger(verbose: bool) -> PathBuf {
  let home_path = home_dir();
  
  if !home_path.is_some() {
    eprintln!("No home directory could be fine. Exiting...");
    std::process::exit(1);
  }

  let mut log_path = home_dir().unwrap();
  log_path.push(format!("{}/{}", CONFIG_DIR_NAME, APP_LOG_FILENAME));

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