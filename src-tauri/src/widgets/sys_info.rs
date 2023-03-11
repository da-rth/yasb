use super::base::ExecOptions;
use super::base::JsonViewerPopupOptions;
use super::base::WidgetCallbacks;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::MutexGuard;
use std::time::Duration;
use sysinfo::ComponentExt;
use sysinfo::CpuExt;
use sysinfo::DiskExt;
use sysinfo::DiskType;
use sysinfo::NetworkExt;
use sysinfo::System;
use sysinfo::SystemExt;
use tauri::State;
use throttle_my_fn::throttle;
use ts_rs::TS;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(rename_all = "snake_case")]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub enum SysInfoCallbackType {
    ToggleLabel,
    JsonViewer,
    Exec(ExecOptions),
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SysInfoWidgetProps {
    class: Option<String>,
    label: Option<String>,
    label_alt: Option<String>,
    label_tooltip: Option<String>,
    interval: Option<i32>,
    json_viewer: Option<JsonViewerPopupOptions>,
    callbacks: Option<WidgetCallbacks<SysInfoCallbackType>>,
}

impl Default for SysInfoWidgetProps {
    fn default() -> SysInfoWidgetProps {
        SysInfoWidgetProps {
            class: None,
            label: None,
            label_alt: None,
            label_tooltip: None,
            interval: None,
            json_viewer: None,
            callbacks: None,
        }
    }
}

pub struct SysInfoSystemState(pub Arc<Mutex<System>>);

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemInformationPayload {
    sys: OperatingSystemInfo,
    mem: SystemMemoryInfo,
    cpus: Vec<SystemCpuInfo>,
    networks: HashMap<String, SystemNetowrkData>,
    components: Vec<SystemComponentsInfo>,
}

#[throttle(1, Duration::from_millis(100))]
fn try_refresh_sys(sys: &mut MutexGuard<System>) {
    sys.refresh_all();
}

#[tauri::command]
pub fn get_sys_info(
    _app_handle: tauri::AppHandle,
    sys_state: State<SysInfoSystemState>,
) -> Option<SystemInformationPayload> {
    let mut lock = sys_state.0.try_lock();
    if let Ok(ref mut sys) = lock {
        // Throttle system refresh to every 100ms
        try_refresh_sys(sys);

        let sys_cpu_info = sys.global_cpu_info();
        let sys_load_avg = sys.load_average();
        let mut disks: Vec<SystemDiskInfo> = Vec::new();
        let mut cpus: Vec<SystemCpuInfo> = Vec::new();
        let mut components: Vec<SystemComponentsInfo> = Vec::new();
        let mut networks: HashMap<String, SystemNetowrkData> = HashMap::new();

        for disk in sys.disks() {
            disks.push(SystemDiskInfo {
                kind: match disk.type_() {
                    DiskType::HDD => "HDD".to_string(),
                    DiskType::SSD => "SSD".to_string(),
                    _ => "unknown".to_string(),
                },
                name: disk.name().to_str().unwrap_or("unknown").to_string(),
                file_system: std::str::from_utf8(disk.file_system())
                    .unwrap_or("unknown")
                    .to_string(),
                mount_point: disk
                    .mount_point()
                    .to_path_buf()
                    .to_str()
                    .unwrap_or("unknown")
                    .to_string(),
                total_space: disk.total_space(),
                available_space: disk.available_space(),
                is_removable: disk.is_removable(),
            });
        }

        for (interface_name, data) in sys.networks() {
            networks.insert(
                interface_name.to_string(),
                SystemNetowrkData {
                    received: data.received(),
                    transmitted: data.transmitted(),
                    total_received: data.total_received(),
                    total_transmitted: data.total_transmitted(),
                },
            );
        }

        for component in sys.components() {
            components.push(SystemComponentsInfo {
                temperature: component.temperature(),
                max: component.max(),
                critical: component.critical(),
                label: component.label().to_string(),
            });
        }

        for cpu in sys.cpus() {
            cpus.push(SystemCpuInfo {
                name: cpu.name().to_string(),
                brand: cpu.brand().to_string(),
                vendor_id: cpu.vendor_id().to_string(),
                frequency: cpu.frequency(),
                cpu_usage: cpu.cpu_usage(),
            });
        }

        Some(SystemInformationPayload {
            mem: SystemMemoryInfo {
                mem_used: sys.used_memory(),
                mem_total: sys.total_memory(),
                swap_used: sys.used_swap(),
                swap_total: sys.total_swap(),
            },
            sys: OperatingSystemInfo {
                name: sys.name(),
                ver: sys.os_version(),
                host: sys.host_name(),
                boot_time: sys.boot_time(),
                uptime: sys.uptime(),
                num_cpus: cpus.len(),
                num_cores: sys.physical_core_count(),
                cpu_info: SystemCpuInfo {
                    name: sys_cpu_info.name().to_string(),
                    brand: sys_cpu_info.brand().to_string(),
                    vendor_id: sys_cpu_info.vendor_id().to_string(),
                    frequency: sys_cpu_info.frequency(),
                    cpu_usage: sys_cpu_info.cpu_usage(),
                },
                load_avg: SystemLoadAverage {
                    one: sys_load_avg.one,
                    five: sys_load_avg.five,
                    fifteen: sys_load_avg.fifteen,
                },
            },
            cpus: cpus,
            components: components,
            networks: networks,
        })
    } else {
        None
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct OperatingSystemInfo {
    pub name: Option<String>,
    pub ver: Option<String>,
    pub host: Option<String>,
    pub boot_time: u64,
    pub uptime: u64,
    pub num_cpus: usize,
    pub num_cores: Option<usize>,
    pub cpu_info: SystemCpuInfo,
    pub load_avg: SystemLoadAverage,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemMemoryInfo {
    pub mem_used: u64,
    pub mem_total: u64,
    pub swap_used: u64,
    pub swap_total: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemLoadAverage {
    pub one: f64,
    pub five: f64,
    pub fifteen: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemComponentsInfo {
    temperature: f32,
    max: f32,
    critical: Option<f32>,
    label: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemDiskInfo {
    kind: String,
    name: String,
    file_system: String,
    mount_point: String,
    total_space: u64,
    available_space: u64,
    is_removable: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemNetowrkData {
    received: u64,
    transmitted: u64,
    total_received: u64,
    total_transmitted: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/widget/sysinfo/")]
pub struct SystemCpuInfo {
    name: String,
    brand: String,
    vendor_id: String,
    frequency: u64,
    cpu_usage: f32,
}
