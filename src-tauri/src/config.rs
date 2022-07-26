use std::path::PathBuf;
use home;
use serde::Deserialize;
use serde::Serialize;


const CONFIG_FILENAME: &str = "config.yaml";

#[derive(Default, Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ConfigYaml {
    pub test: String,
}

pub fn get_config_path() -> PathBuf {
    let home_path = home::home_dir();

    if let Some(home_dir) = home_path {
        let home_config = home_dir.join(".yasb").join(CONFIG_FILENAME);

        if home_config.exists() {
            return home_config
        }
    }

    PathBuf::from(CONFIG_FILENAME)
}

// pub fn read_config(config_path: PathBuf) -> Result<ConfigYaml, anyhow::Error> {
//     let config: YamlConfig =serde_yaml::from_str(&std::fs::read_to_string(config_path)?)?
// }