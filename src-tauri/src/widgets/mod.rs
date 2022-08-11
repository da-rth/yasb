mod base;
pub mod custom;

use serde::{Serialize, Deserialize};


#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum ConfiguredWidget {
    TextWidget {
      class: Option<String>,
      text: Option<String>
    },
    DateTimeWidget {
      class: Option<String>,
      format: Option<String>,
      interval: Option<u32>
    },
    CustomWidget {
      class: Option<String>,
      label: String,
      label_alt: Option<String>,
      command: Option<custom::CommandOptions>,
      callbacks: Option<base::WidgetCallbacks>
    }
}
