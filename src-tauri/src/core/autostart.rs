use std::path::Path;
use winreg::enums::*;
use winreg::RegKey;

use super::constants::APP_REG_NAME;

const HKCU: RegKey = RegKey::predef(HKEY_CURRENT_USER);

fn get_key() -> RegKey {
    let autorun_path = Path::new("Software\\Microsoft\\Windows\\CurrentVersion\\Run");
    let (key, _disp) = HKCU.create_subkey(autorun_path).unwrap();
    key
}

pub fn autostart_key_exists() -> bool {
    let key = get_key();
    let value: std::io::Result<String> = key.get_value(APP_REG_NAME);
    value.is_ok()
}

pub fn delete_autostart_key() -> () {
    let key = get_key();
    key.delete_value(APP_REG_NAME).unwrap();
}

pub fn add_autostart_key() -> () {
    let key = get_key();
    let current_exe = std::env::current_exe().unwrap();
    let quot_exe = format!("\"{}\"", &current_exe.to_str().unwrap());
    key.set_value(APP_REG_NAME, &quot_exe).unwrap();
}
