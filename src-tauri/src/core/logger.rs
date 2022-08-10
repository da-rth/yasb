use std::{fs::{File, create_dir_all}, path::PathBuf};
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
  if let Some(home_path) = home_dir() {

    let mut log_path = home_path;
    log_path.push(CONFIG_DIR_NAME);
    log_path.push(APP_LOG_FILENAME);

    create_dir_all(log_path.parent().unwrap()).unwrap_or_else(|_| {
      eprintln!("Error creating logger directory");
    });

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
  } else {
    eprintln!("No home directory could be fine. Exiting...");
    std::process::exit(1);
  }
}
