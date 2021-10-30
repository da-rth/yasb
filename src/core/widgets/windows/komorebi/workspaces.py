import traceback
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
from typing import Literal
from core.utils.windows import get_monitor_hwnd
from core.event_service import EventService
from core.event_enums import BarEvent, KomorebiEvent
from core.widgets.base import BaseWidget
from core.widgets.windows.komorebi.helpers.client import KomorebiClient


WorkspaceState = Literal["EMPTY", "POPULATED", "ACTIVE"]
WORKSPACE_STATE_EMPTY: WorkspaceState = "EMPTY"
WORKSPACE_STATE_POPULATED: WorkspaceState = "POPULATED"
WORKSPACE_STATE_ACTIVE: WorkspaceState = "ACTIVE"


class WorkspaceButton(QPushButton):

    def __init__(self, workspace_index: int, label: str = None):
        super().__init__()
        self.komorebic = KomorebiClient()
        self.workspace_index = workspace_index
        self.state = WORKSPACE_STATE_EMPTY
        self.setProperty("class", "ws-btn")
        self.setText(label if label else str(workspace_index + 1))
        self.clicked.connect(self.activate_workspace)

    def update_state_and_redraw(self, state: WorkspaceState):
        self.state = state
        self.setProperty("class", f"ws-btn {state.lower()}")

    def activate_workspace(self):
        try:
            self.komorebic.activate_workspace(self.workspace_index)
        except Exception:
            print(f"Failed to focus workspace at index {self.workspace_index}")


class WorkspaceWidget(BaseWidget):
    k_signal_connect = pyqtSignal(dict)
    k_signal_update = pyqtSignal(dict)
    k_signal_disconnect = pyqtSignal()
    k_signal_focus_change = pyqtSignal(dict)
    k_signal_workspace_focus = pyqtSignal(dict)

    def __init__(
            self,
            offline_status_label: str = "komorebi offline"
    ):
        super().__init__(class_name="komorebi-workspaces")
        self._event_service = EventService()
        self._komorebic = KomorebiClient()
        self._komorebi_screen = None
        self._komorebi_workspaces = []
        self._prev_workspace_index = None
        self._curr_workspace_index = None
        self._workspace_buttons: list[QPushButton] = []

        # Disable default mouse event handling inherited from BaseWidget
        self.mousePressEvent = None

        # Status text shown when komorebi state can't be retrieved
        self._offline_text = QLabel()
        self._offline_text.setText(offline_status_label)
        self._offline_text.setProperty("class", "offline-status")

        # Construct container which holds workspace buttons
        self._workspace_container_layout: QHBoxLayout = QHBoxLayout()
        self._workspace_container_layout.setSpacing(0)
        self._workspace_container_layout.setContentsMargins(0, 0, 0, 0)
        self._workspace_container_layout.addWidget(self._offline_text)
        self._workspace_container: QWidget = QWidget()
        self._workspace_container.setLayout(self._workspace_container_layout)
        self._workspace_container.setProperty("class", "komorebi-workspaces-container")
        self._workspace_container.hide()

        self.widget_layout.addWidget(self._offline_text)
        self.widget_layout.addWidget(self._workspace_container)
        self._register_signals_and_events()

    def _register_signals_and_events(self):
        self.k_signal_connect.connect(self._on_komorebi_connect_event)
        self.k_signal_update.connect(self._on_komorebi_update_event)
        self.k_signal_disconnect.connect(self._on_komorebi_disconnect_event)
        self.k_signal_focus_change.connect(self._on_komorebi_focus_change_event)
        self.k_signal_workspace_focus.connect(self._on_komorebi_focus_change_event)

        self._event_service.register_event(KomorebiEvent.KomorebiConnect,  self.k_signal_connect)
        self._event_service.register_event(KomorebiEvent.KomorebiUpdate, self.k_signal_update)
        self._event_service.register_event(KomorebiEvent.KomorebiDisconnect, self.k_signal_disconnect)
        self._event_service.register_event(KomorebiEvent.FocusChange, self.k_signal_focus_change)
        self._event_service.register_event(KomorebiEvent.FocusWorkspaceNumber, self.k_signal_workspace_focus)

    def _reset(self):
        self._komorebi_state = None
        self._komorebi_screen = None
        self._komorebi_workspaces = []
        self._curr_workspace_index = None
        self._prev_workspace_index = None
        self._workspace_buttons = []
        self._clear_container_layout()

    def _clear_container_layout(self):
        for i in reversed(range(self._workspace_container_layout.count())):
            old_workspace_widget = self._workspace_container_layout.itemAt(i).widget()
            self._workspace_container_layout.removeWidget(old_workspace_widget)
            old_workspace_widget.setParent(None)

    def _on_komorebi_connect_event(self, state: dict) -> None:
        self._reset()
        self._hide_offline_status()
        self._update_status_and_buttons(state)

    def _on_komorebi_update_event(self, state: dict) -> None:
        self._update_status_and_buttons(state)

    def _on_komorebi_disconnect_event(self) -> None:
        self._show_offline_status()

    def _on_komorebi_focus_change_event(self, event_content: dict) -> None:
        state = event_content.get('state', None)
        self._update_status_and_buttons(state)

    def _update_status_and_buttons(self, state: dict):
        try:
            if self._update_komorebi_state(state):
                if self._update_workspace_indexes():
                    self._update_workspace_buttons()
            elif self._offline_text.isHidden():
                self._show_offline_status()
        except Exception:
            print(traceback.format_exc())

    def _update_komorebi_state(self, komorebi_state: dict):
        try:
            self._screen_hwnd = get_monitor_hwnd(int(QWidget.winId(self)))
            self._komorebi_state = komorebi_state
            if self._komorebi_state:
                self._komorebi_screen = self._komorebic.get_screen_by_hwnd(self._komorebi_state, self._screen_hwnd)
                self._komorebi_workspaces = self._komorebic.get_workspaces(self._komorebi_screen)
                return True
        except TypeError:
            # Monitor for widget hwnd no longer exists
            self._event_service.emit_event(BarEvent.CloseBar,  self.bar_index)
        return False

    def _update_workspace_indexes(self) -> bool:
        focused_workspace = self._komorebic.get_focused_workspace(self._komorebi_screen)

        if focused_workspace['index'] != self._curr_workspace_index:
            self._prev_workspace_index = self._curr_workspace_index
            self._curr_workspace_index = focused_workspace['index']
            return True

        return False

    def _update_workspace_buttons(self) -> None:

        for workspace_index, workspace in enumerate(self._komorebi_workspaces):
            try:
                ws_btn = self._workspace_buttons[workspace_index]
            except IndexError:
                ws_btn = self._try_add_workspace_button(workspace_index)

            if ws_btn:
                self._update_button_state(ws_btn)

        self._workspace_container.setStyleSheet('')

    def _try_add_workspace_button(self, workspace_index: int) -> QPushButton:
        workspace_button_indexes = [ws_btn.workspace_index for ws_btn in self._workspace_buttons]

        if workspace_index not in workspace_button_indexes:
            workspace_btn = WorkspaceButton(workspace_index)
            self._update_button_state(workspace_btn)
            self._workspace_buttons.append(workspace_btn)
            self._clear_container_layout()

            for workspace_btn in self._workspace_buttons:
                self._workspace_container_layout.addWidget(workspace_btn)

            return workspace_btn

    def _update_button_state(self, workspace_btn: QPushButton) -> None:
        workspace_index = workspace_btn.workspace_index
        workspace = self._komorebic.get_workspace_by_index(self._komorebi_screen, workspace_index)

        if self._curr_workspace_index == workspace_index:
            btn_state = WORKSPACE_STATE_ACTIVE
        elif self._komorebic.workspace_has_windows(workspace) > 0:
            btn_state = WORKSPACE_STATE_POPULATED
        else:
            btn_state = WORKSPACE_STATE_EMPTY

        workspace_btn.update_state_and_redraw(btn_state)

    def _show_offline_status(self):
        self._offline_text.show()
        self._workspace_container.hide()

    def _hide_offline_status(self):
        self._offline_text.hide()
        self._workspace_container.show()
