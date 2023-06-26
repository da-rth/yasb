import logging
from collections import deque
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import pyqtSignal
from ...utils.win32.utilities import get_monitor_hwnd
from ...event_service import EventService
from ...event_enums import KomorebiEvent
from ..base import BaseWidget
from ...utils.komorebi.client import KomorebiClient
from ...validation.widgets.komorebi.active_layout import VALIDATION_SCHEMA

try:
    from ...utils.komorebi.event_listener import KomorebiEventListener
except ImportError:
    KomorebiEventListener = None
    logging.warning("Failed to load Komorebi Event Listener")

layout_cmds = {
    "BSP": "bsp",
    "Columns": "columns",
    "Rows": "rows",
    "VerticalStack": "vertical-stack",
    "HorizontalStack": "horizontal-stack",
    "UltrawideVerticalStack": "ultrawide-vertical-stack"
}

layout_snake_case = {
    "BSP": "bsp",
    "Columns": "columns",
    "Rows": "rows",
    "VerticalStack": "vertical_stack",
    "HorizontalStack": "horizontal_stack",
    "UltrawideVerticalStack": "ultrawide_vertical_stack"
}


class ActiveLayoutWidget(BaseWidget):
    k_signal_connect = pyqtSignal(dict)
    k_signal_disconnect = pyqtSignal()
    k_signal_layout_change = pyqtSignal(dict, dict)

    validation_schema = VALIDATION_SCHEMA
    event_listener = KomorebiEventListener

    def __init__(self, label: str, layout_icons: dict[str, str], hide_if_offline: bool, callbacks: dict[str, str]):
        super().__init__(class_name="komorebi-active-layout")
        self._label = label
        self._layout_icons = layout_icons
        self._layouts = deque([
            'bsp', 'columns', 'rows', 'vertical-stack', 'horizontal-stack', 'ultrawide-vertical-stack'
        ])
        self._hide_if_offline = hide_if_offline
        self._event_service = EventService()
        self._komorebic = KomorebiClient()
        self._komorebi_screen = None
        self._komorebi_workspaces = []
        self._focused_workspace = {}

        self._active_layout_text = QLabel()
        self._active_layout_text.setProperty("class", "label")
        self._active_layout_text.hide()

        self.widget_layout.addWidget(self._active_layout_text)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']

        self.register_callback("next_layout", self._next_layout)
        self.register_callback("prev_layout", self._prev_layout)
        self.register_callback("flip_layout", self._komorebic.flip_layout)
        self.register_callback("toggle_tiling", lambda: self._komorebic.toggle("tiling"))
        self.register_callback("toggle_float", lambda: self._komorebic.toggle("float"))
        self.register_callback("toggle_monocle", lambda: self._komorebic.toggle("monocle"))
        self.register_callback("toggle_maximise", lambda: self._komorebic.toggle("maximise"))
        self.register_callback("toggle_pause", lambda: self._komorebic.toggle("pause"))

        self._register_signals_and_events()

    def _next_layout(self):
        if self._is_shift_layout_allowed():
            self._layouts.rotate(1)
            self._komorebic.change_layout(self._layouts[0])

    def _prev_layout(self):
        if self._is_shift_layout_allowed():
            self._layouts.rotate(-1)
            self._komorebic.change_layout(self._layouts[0])

    def _is_shift_layout_allowed(self):
        return not bool(
            not self._focused_workspace.get('tile', False) or
            self._focused_workspace.get('monocle_container', None) or
            self._focused_workspace.get('maximized_window', None) or
            self._komorebi_state.get('is_paused', False)
        )

    def _register_signals_and_events(self):
        active_layout_change_event_watchlist = [
            KomorebiEvent.ChangeLayout,
            KomorebiEvent.TogglePause,
            KomorebiEvent.ToggleTiling,
            KomorebiEvent.ToggleMonocle,
            KomorebiEvent.ToggleMaximise
        ]

        self.k_signal_connect.connect(self._on_komorebi_connect_event)
        self.k_signal_disconnect.connect(self._on_komorebi_disconnect_event)
        self.k_signal_layout_change.connect(self._on_komorebi_layout_change_event)

        self._event_service.register_event(KomorebiEvent.KomorebiConnect,  self.k_signal_connect)
        self._event_service.register_event(KomorebiEvent.KomorebiDisconnect, self.k_signal_disconnect)

        for event_type in active_layout_change_event_watchlist:
            self._event_service.register_event(event_type, self.k_signal_layout_change)

    def _on_komorebi_connect_event(self, state: dict) -> None:
        self._update_active_layout(state, is_connect_event=True)

    def _on_komorebi_layout_change_event(self, _event: dict, state: dict) -> None:
        self._update_active_layout(state)

    def _on_komorebi_disconnect_event(self) -> None:
        if self._hide_if_offline:
            self._active_layout_text.hide()

    def _update_active_layout(self, state: dict, is_connect_event=False):
        try:
            if self._update_komorebi_state(state):
                self._focused_workspace = self._komorebic.get_focused_workspace(self._komorebi_screen)

                if not self._focused_workspace:
                    return

                layout_name, layout_icon = self._get_layout_label_info()

                if is_connect_event:
                    conn_layout_name = self._focused_workspace['layout']['Default']
                    conn_layout_cmd = layout_cmds.get(conn_layout_name, 'bsp')

                    while self._layouts[0] != conn_layout_cmd:
                        self._layouts.rotate(1)

                self._active_layout_text.setText(
                    self._label.replace("{icon}", layout_icon).replace("{layout_name}", layout_name)
                )

                if self._active_layout_text.isHidden():
                    self._active_layout_text.show()
        except Exception:
            logging.exception("Failed to update komorebi status and widget button state")

    def _get_layout_label_info(self):
        if self._komorebi_state.get('is_paused', False):
            layout_name = 'Paused'
            layout_icon = self._layout_icons['paused']
        elif not self._focused_workspace.get('tile', False):
            layout_name = 'Floating'
            layout_icon = self._layout_icons['floating']
        elif self._focused_workspace.get('maximized_window', None):
            layout_name = 'Maximised'
            layout_icon = self._layout_icons['maximised']
        elif self._focused_workspace.get('monocle_container', None):
            layout_name = 'Monocle'
            layout_icon = self._layout_icons['monocle']
        else:
            layout_name = self._focused_workspace['layout']['Default']
            layout_icon = self._layout_icons.get(layout_snake_case[layout_name], 'unknown layout')

        return layout_name, layout_icon

    def _update_komorebi_state(self, komorebi_state: dict):
        try:
            self._screen_hwnd = get_monitor_hwnd(int(QWidget.winId(self)))
            self._komorebi_state = komorebi_state

            if self._komorebi_state:
                self._komorebi_screen = self._komorebic.get_screen_by_hwnd(self._komorebi_state, self._screen_hwnd)
                self._komorebi_workspaces = self._komorebic.get_workspaces(self._komorebi_screen)
                return True
        except TypeError:
            return False
