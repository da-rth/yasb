use serde::{Deserialize, Serialize};
use std::os::windows::process::CommandExt;
use std::{
    io::{Error, Read},
    process::{Child, Command, Stdio},
    time::Duration,
};
use ts_rs::TS;
use wait_timeout::ChildExt;

use super::base::WidgetCallbacks;

const CREATE_NO_WINDOW: u32 = 0x08000000;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/custom/")]
pub struct CustomWidgetProps {
    class: Option<String>,
    label: Option<String>,
    label_alt: Option<String>,
    command: Option<CustomCommandOptions>,
    callbacks: Option<WidgetCallbacks>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/custom/")]
pub struct CustomCommandOptions {
    cmd: String,
    args: Option<Vec<String>>,
    interval: Option<u32>,
    timeout: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/custom/")]
pub struct CustomCommandResponse {
    stdout: Option<String>,
    stderr: Option<String>,
    status: Option<i32>,
}

#[tauri::command]
pub fn process_custom_command(
    command: String,
    args: Vec<String>,
    timeout: u64,
) -> CustomCommandResponse {
    let mut cmd = Command::new(command.clone());
    cmd.args(args.clone());
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());
    cmd.creation_flags(CREATE_NO_WINDOW);

    match cmd.spawn() {
        Ok(child) => process_child(child, timeout),
        Err(e) => process_error(command, args, e),
    }
}

fn process_child(mut child: Child, timeout: u64) -> CustomCommandResponse {
    let timeout = Duration::from_millis(timeout);

    let status = match child.wait_timeout(timeout).unwrap() {
        Some(status) => status.code(),
        None => {
            child.kill().unwrap();
            child.wait().unwrap().code()
        }
    };

    let stdout = match child.stdout {
        Some(mut out) => {
            let mut stdout_buf = String::new();
            let _ = out.read_to_string(&mut stdout_buf);
            Some(stdout_buf)
        }
        None => None,
    };

    let stderr = match child.stderr {
        Some(mut err) => {
            let mut stderr_buf = String::new();
            let _ = err.read_to_string(&mut stderr_buf);
            Some(stderr_buf)
        }
        None => None,
    };

    CustomCommandResponse {
        stdout,
        stderr,
        status,
    }
}

fn process_error(cmd: String, args: Vec<String>, error: Error) -> CustomCommandResponse {
    log::error!(
        "Error processing CustomWidget command: {} {:?}: {}",
        cmd,
        args,
        error
    );
    CustomCommandResponse {
        stdout: None,
        stderr: Some(error.to_string()),
        status: Some(1),
    }
}
