use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum ConfiguredWidget {
    TextWidget {
      class: Option<String>,
      text: Option<String>,
      href: Option<String>
    },
    DateTimeWidget {
      class: Option<String>,
      format: Option<String>,
      interval: Option<u32>
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum BarWidget {
  Configured(ConfiguredWidget),
  Default {
    kind: String
  }
}