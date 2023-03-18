use std::process::{Command, ExitStatus, Stdio};

use crate::core::constants::APP_NAME;

const KOMOREBI_CLI_EXE: &str = "komorebic.exe";

pub fn subscribe(pipe_name: &str) -> ExitStatus {
    let mut child = Command::new(KOMOREBI_CLI_EXE)
        .arg("subscribe")
        .arg(pipe_name)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .unwrap();
    child.wait().unwrap()
}

pub fn unmanage_app_exe() -> ExitStatus {
    let mut child = Command::new(KOMOREBI_CLI_EXE)
        .arg("float-rule")
        .arg("exe")
        .arg(format!("{}.exe", APP_NAME))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .unwrap();
    child.wait().unwrap()
}

pub fn query_state() -> ExitStatus {
    let mut child = Command::new(KOMOREBI_CLI_EXE)
        .arg("state")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .unwrap();
    child.wait().unwrap()
}