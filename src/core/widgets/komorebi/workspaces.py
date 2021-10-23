from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel
from ..base import BaseWidget
from .komorebi_client import KomorebiClient
from typing import Literal


komorebic = KomorebiClient()
WorkspaceState = Literal["EMPTY", "POPULATED", "ACTIVE"]
WORKSPACE_STATE_EMPTY: WorkspaceState = "EMPTY"
WORKSPACE_STATE_POPULATED: WorkspaceState = "POPULATED"
WORKSPACE_STATE_ACTIVE: WorkspaceState = "ACTIVE"


class WorkspaceButton(QPushButton):

    def __init__(self, idx: int, label: str):
        super().__init__()
        self.ws_idx = idx
        self.state = WORKSPACE_STATE_EMPTY
        self.setProperty("class", "ws-btn")
        self.setText(label)
        self.clicked.connect(self.activate_workspace)

    def update_state_and_redraw(self, state: WorkspaceState):
        self.state = state
        self.setProperty("class", f"ws-btn {state.lower()}")
        self.setStyleSheet(self.styleSheet())

    def activate_workspace(self):
        komorebic.activate_workspace(self.ws_idx)


class WorkspaceWidget(BaseWidget):

    def __init__(
            self,
            timer_interval: int = 2000,
            class_name: str = "komorebi-workspaces"
    ):
        super().__init__(timer_interval, class_name)
        self._screen_idx = 0
        self._workspace_buttons: list[QPushButton] = []
        self._workspace_container: QWidget = QWidget()
        self._focused_workspace_idx = None

        # Disable mouse event handling from BaseWidget
        self.mousePressEvent = None

        self._offline_text = QLabel()
        self._offline_text.setText("komorebi offline")
        self._offline_text.setProperty("class", "komorebi-offline")
        self._offline_text.hide()

        self._workspace_container_layout: QHBoxLayout = QHBoxLayout()
        self._workspace_container_layout.setSpacing(0)
        self._workspace_container_layout.setContentsMargins(0, 0, 0, 0)
        self._workspace_container.setLayout(self._workspace_container_layout)
        self._workspace_container.setProperty("class", "komorebi-workspaces")

        self.layout.addWidget(self._offline_text)
        self.layout.addWidget(self._workspace_container)

        # NOTE: Currently every N seconds we call update_workspaces via a QTimer
        # This method will hopefully be replaced by an event listener which listens to komorebi's public socket
        self.register_callback("update_workspaces", self._update_workspace_buttons)
        self.callback_timer: str = "update_workspaces"

        self._build_workspace_buttons()
        self.start_timer()

    def _build_workspace_buttons(self):
        komorebic.update_state()

        self._update_komorebi_offline_status()

        if komorebic.state:
            workspaces = komorebic.get_workspaces(self._screen_idx)
            self._focused_workspace_idx = komorebic.get_focused_workspace_idx(self._screen_idx)

            for ws_idx, workspace in enumerate(workspaces):
                self._add_workspace_button(ws_idx)

            self._workspace_container_layout.addWidget(self._workspace_container)

    def _update_workspace_buttons(self):
        komorebic.update_state()

        self._update_komorebi_offline_status()

        if komorebic.state:
            workspaces = komorebic.get_workspaces(screen_idx=self._screen_idx)
            self._focused_workspace_idx = komorebic.get_focused_workspace_idx(self._screen_idx)

            for ws_idx, workspace in enumerate(workspaces):
                try:
                    ws_btn = self._workspace_buttons[ws_idx]
                except IndexError:
                    ws_btn = self._add_workspace_button(ws_idx)

                self._update_button_state(ws_btn)

    def _update_komorebi_offline_status(self):
        if komorebic.state:
            self._offline_text.hide()
            self._workspace_container.show()
        else:
            self._offline_text.show()
            self._workspace_container.hide()

    def _add_workspace_button(self, ws_idx):
        ws_btn = WorkspaceButton(idx=ws_idx, label=str(ws_idx + 1))
        self._update_button_state(ws_btn)
        self._workspace_buttons.append(ws_btn)
        self._workspace_container_layout.addWidget(ws_btn)
        return ws_btn

    def _update_button_state(self, ws_btn):
        button_workspace_idx = ws_btn.ws_idx

        if self._focused_workspace_idx == button_workspace_idx:
            btn_state = WORKSPACE_STATE_ACTIVE
        elif komorebic.get_workspace_num_windows(self._screen_idx, button_workspace_idx) > 0:
            btn_state = WORKSPACE_STATE_POPULATED
        else:
            btn_state = WORKSPACE_STATE_EMPTY

        ws_btn.update_state_and_redraw(state=btn_state)
