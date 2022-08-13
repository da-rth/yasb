use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/cat/")]
pub struct CatWidgetProps {
    class: Option<String>,
    label: Option<String>,
    target: Option<CatCommandOptions>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/cat/")]
pub struct CatCommandOptions {
    file: String,
    interval: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/cat/")]
pub struct CatCommandResponse {
    stdout: Option<String>,
    stderr: Option<String>,
    status: Option<i32>,
}

#[tauri::command]
pub fn process_cat_command(target: String) -> CatCommandResponse {
    let path = match shellexpand::full(&target) {
        Ok(expanded) => expanded.to_string(),
        Err(_) => target,
    };

    match std::fs::read_to_string(&path) {
        Ok(output) => CatCommandResponse {
            stdout: Some(output),
            stderr: None,
            status: None,
        },
        Err(e) => CatCommandResponse {
            stderr: Some(e.to_string()),
            stdout: None,
            status: None,
        },
    }
}
