use super::configuration::BarEdge;

pub const FRONTEND_SETUP: &str = "setup.html";
pub const FRONTEND_INDEX: &str = "index.html";

pub const APP_LOG_FILENAME: &str = "yasb.log";
pub const CONFIG_DIR_NAME: &str = "yasb";
pub const CONFIG_FILENAME: &str = "config.yaml";
pub const STYLES_FILENAME: &str = "styles.scss";

pub const DEFAULT_BAR_THICKNESS: u32 = 64;
pub const DEFAULT_BAR_EDGE: BarEdge = BarEdge::Top;
pub const DEFAULT_BAR_TRANSPARENCY: bool = true;
pub const DEFAULT_BAR_WINAPPBAR: bool = true;

pub const CLI_ARG_CONFIG: &str = "config";
pub const CLI_ARG_STYLES: &str = "styles";
pub const CLI_ARG_VERBOSE: &str = "verbose";
pub const CLI_ARG_VERSION: &str = "version";
pub const CLI_ARG_HELP: &str = "help";

pub const IGNORED_FULLSCREEN_CLASSES: &'static [&'static str] = &[
    "SHELLDLL_DefView",
    "WorkerW",
    "XamlExplorerHostIslandWindow",
];
