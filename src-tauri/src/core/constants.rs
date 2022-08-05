use super::configuration::BarEdge;
use strum_macros;

pub const FRONTEND_SETUP: &str = "setup.html";
pub const FRONTEND_INDEX: &str = "index.html";

pub const APPLICATION_LOG_FILENAME: &str = "yasb.log";
pub const APPLICATION_NAME: &str = "Yasb";
pub const APPLICATION_IDENTIFIER: &str = "com.github.denbot.yasb";

pub const CONFIG_DIR_NAME: &str = ".yasb";
pub const CONFIG_FILENAME: &str = "config.yaml";
pub const STYLES_FILENAME: &str = "styles.scss";

pub const DEFAULT_BAR_THICKNESS: u32 = 64;
pub const DEFAULT_BAR_EDGE: BarEdge = BarEdge::Top;

#[derive(strum_macros::Display)]
pub enum Event {
  StylesChangedEvent
}
