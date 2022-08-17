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
#[ts(export, export_to = "../src/bindings/widget/events/")]
pub enum ActiveWindowWidgetEvents {
    ForegroundChanged,
}

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
#[ts(export, export_to = "../src/bindings/widget/events/index.ts")]
pub enum WidgetEvent {
    ActiveWindowWidget(ActiveWindowWidgetEvents),
}
