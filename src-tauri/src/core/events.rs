#[derive(
    Debug,
    Clone,
    PartialEq,
    Eq,
    serde::Serialize,
    serde::Deserialize,
    ts_rs::TS,
    strum_macros::Display,
)]
#[ts(export, export_to = "../src/bindings/config/")]
pub enum BarEvent {
    HideWindowEvent,
    HideAllWindowsEvent,
    ShowWindowEvent,
    ShowAllWindowsEvent,
    StylesChangedEvent,
}
