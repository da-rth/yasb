use std::os::windows::process::CommandExt;
use std::process::ExitStatus;
use std::process::{Command, Stdio};

use crate::core::constants::APP_NAME;

const KOMOREBI_CLI_EXE: &str = "komorebic.exe";
const CREATE_NO_WINDOW: u32 = 0x08000000;

pub fn subscribe(pipe_name: &str) -> ExitStatus {
    let mut cmd = Command::new(KOMOREBI_CLI_EXE);
    cmd.arg("subscribe");
    cmd.arg(pipe_name);
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd.spawn().unwrap().wait().unwrap()
}

pub fn unmanage_app_exe() -> ExitStatus {
    let mut cmd = Command::new(KOMOREBI_CLI_EXE);
    cmd.arg("float-rule");
    cmd.arg("exe");
    cmd.arg(format!("{}.exe", APP_NAME));
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd.spawn().unwrap().wait().unwrap()
}
