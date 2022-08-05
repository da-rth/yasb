use super::configuration::BarEdge;
use strum_macros;

pub const FRONTEND_SETUP: &str = "setup.html";
pub const FRONTEND_INDEX: &str = "index.html";

pub const APP_LOG_FILENAME: &str = "yasb.log";
pub const CONFIG_DIR_NAME: &str = ".yasb";
pub const CONFIG_FILENAME: &str = "config.yaml";
pub const STYLES_FILENAME: &str = "styles.scss";

pub const DEFAULT_BAR_THICKNESS: u32 = 64;
pub const DEFAULT_BAR_EDGE: BarEdge = BarEdge::Top;

#[derive(strum_macros::Display)]
pub enum Event {
  StylesChangedEvent
}
