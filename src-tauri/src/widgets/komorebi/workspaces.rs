use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/komorebi/")]
pub struct KomorebiWorkspaceProps {
    label: Option<String>,
    label_offline: Option<String>,
    label_tooltip: Option<String>,
    hide_empty: Option<bool>,
    cycle_on_scroll: Option<bool>,
}

impl Default for KomorebiWorkspaceProps {
    fn default() -> KomorebiWorkspaceProps {
        KomorebiWorkspaceProps {
            label: None,
            label_offline: None,
            label_tooltip: None,
            hide_empty: None,
            cycle_on_scroll: None,
        }
    }
}
