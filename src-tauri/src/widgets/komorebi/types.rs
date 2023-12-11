use komorebi_core::{
    Axis, FocusFollowsMouseImplementation, Layout, MoveBehaviour, Rect, SocketMessage, WindowContainerBehaviour,
};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

use super::winevent::WinEvent;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Ring<T> {
    elements: VecDeque<T>,
    focused: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum NotificationEvent {
    WindowManager(WindowManagerEvent),
    Socket(SocketMessage),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "content")]
pub enum WindowManagerEvent {
    Destroy(WinEvent, Window),
    FocusChange(WinEvent, Window),
    Hide(WinEvent, Window),
    Cloak(WinEvent, Window),
    Minimize(WinEvent, Window),
    Show(WinEvent, Window),
    Uncloak(WinEvent, Window),
    MoveResizeStart(WinEvent, Window),
    MoveResizeEnd(WinEvent, Window),
    MouseCapture(WinEvent, Window),
    Manage(Window),
    Unmanage(Window),
    Raise(Window),
    DisplayChange(Window),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KomorebiNotification {
    pub event: NotificationEvent,
    pub state: KomorebiState,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Window {
    pub(crate) hwnd: isize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Container {
    // #[serde(skip_serializing)]
    // id: String,
    windows: Ring<Window>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Monitor {
    id: isize,
    name: String,
    size: Rect,
    work_area_size: Rect,
    work_area_offset: Option<Rect>,
    workspaces: Ring<Workspace>,
    // #[serde(skip_serializing)]
    // workspace_names: HashMap<usize, String>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Workspace {
    name: Option<String>,
    containers: Ring<Container>,
    monocle_container: Option<Container>,
    // #[serde(skip_serializing)]
    // monocle_container_restore_idx: Option<usize>,
    maximized_window: Option<Window>,
    // #[serde(skip_serializing)]
    // maximized_window_restore_idx: Option<usize>,
    floating_windows: Vec<Window>,
    layout: Layout,
    layout_rules: Vec<(usize, Layout)>,
    layout_flip: Option<Axis>,
    workspace_padding: Option<i32>,
    container_padding: Option<i32>,
    // #[serde(skip_serializing)]
    // latest_layout: Vec<Rect>,
    resize_dimensions: Vec<Option<Rect>>,
    tile: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KomorebiState {
    pub monitors: Ring<Monitor>,
    pub is_paused: bool,
    pub invisible_borders: Rect,
    pub resize_delta: i32,
    pub new_window_behaviour: WindowContainerBehaviour,
    pub cross_monitor_move_behaviour: MoveBehaviour,
    pub work_area_offset: Option<Rect>,
    pub focus_follows_mouse: Option<FocusFollowsMouseImplementation>,
    pub mouse_follows_focus: bool,
    pub has_pending_raise_op: bool,
    pub float_identifiers: Vec<KomorebiIdentifier>,
    pub manage_identifiers: Vec<KomorebiIdentifier>,
    pub layered_whitelist: Vec<KomorebiIdentifier>,
    pub tray_and_multi_window_identifiers: Vec<KomorebiIdentifier>,
    pub border_overflow_identifiers: Vec<KomorebiIdentifier>,
    pub name_change_on_launch_identifiers: Vec<KomorebiIdentifier>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KomorebiIdentifier {
    id: String,
    // These below should probably be enums but this is working for now
    kind: String,
    matching_strategy: String
}
