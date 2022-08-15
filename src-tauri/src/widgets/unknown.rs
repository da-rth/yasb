#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize, ts_rs::TS)]
#[ts(export, export_to = "../src/bindings/widget/unknown/")]
pub struct UnknownWidgetProps {
    pub kind: String,
}
