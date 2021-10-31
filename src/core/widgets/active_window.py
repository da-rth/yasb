import traceback

from core.utils.win32.windows import WinEvent
from core.widgets.base import BaseWidget
from core.event_service import EventService
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel
from typing import Union
from core.bar import BAR_WM_TITLE

IGNORED_TITLES = ['']
IGNORED_CLASSES = ['WorkerW']
IGNORED_PROCESSES = ['SearchHost.exe']
IGNORED_YASB_TITLES = [BAR_WM_TITLE]

DEFAULT_ALT_LABEL = "[class_name='{win[class_name]}' exe='{win[process][name]}' " \
                    "hwnd={win[hwnd]} monitor='{win[monitor_info][device]}']"


class ActiveWindowWidget(BaseWidget):
    foreground_change = pyqtSignal(dict)

    def __init__(
            self,
            label: str = "{win[title]}",
            label_alt: str = DEFAULT_ALT_LABEL,
            on_left: Union[str, list[str]] = "toggle_window_title_text",
            on_middle: Union[str, list[str]] = "toggle_window_title_text",
            on_right: Union[str, list[str]] = "toggle_window_title_text",
            no_window_text: str = "",
            monitor_exclusive_label: bool = True,
            max_title_length: int = None,
            max_title_ellipsis_fmt: str = "..."
    ):
        super().__init__(class_name="active-window-widget")
        self._win_info = None
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._active_label = label
        self._no_window_text = no_window_text
        self._monitor_exclusive_label = monitor_exclusive_label
        self._max_title_length = max_title_length
        self._max_title_ellipsis_fmt = max_title_ellipsis_fmt
        self._event_service = EventService()
        self._window_title_text = QLabel()
        self._window_title_text.setProperty("class", "active-window-label")
        self._window_title_text.setText(self._no_window_text)

        self.widget_layout.addWidget(self._window_title_text)
        self.foreground_change.connect(self._on_focus_change_event)
        self.register_callback("toggle_window_title_text", self._toggle_title_text)

        self.callback_left = on_left
        self.callback_right = on_right
        self.callback_middle = on_middle

        self._event_service.register_event(WinEvent.EventSystemForeground, self.foreground_change)
        self._event_service.register_event(WinEvent.EventSystemMoveSizeEnd, self.foreground_change)
        self._event_service.register_event(WinEvent.EventObjectNameChange, self.foreground_change)

    def _toggle_title_text(self) -> None:
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        print("before", self._win_info)
        self._update_text()

    def _on_focus_change_event(self, win_info: dict) -> None:
        try:
            if win_info['title'] not in IGNORED_YASB_TITLES:
                self._update_window_title(win_info)
        except Exception:
            print(traceback.format_exc())

    def _update_window_title(self, win_info: dict) -> None:
        try:
            hwnd = win_info['hwnd']
            event = win_info['event']
            title = win_info['title']
            process = win_info['process']
            class_name = win_info['class_name']
            monitor_name = win_info['monitor_info'].get('device', None)

            if not hwnd or (event == WinEvent.EventObjectNameChange and not title):
                return
            elif self._monitor_exclusive_label and self.screen().name() != monitor_name:
                return self._window_title_text.hide()
            elif (title in IGNORED_TITLES) or (class_name in IGNORED_CLASSES) or (process in IGNORED_PROCESSES):
                if not self._no_window_text:
                    return self._window_title_text.hide()
            else:
                if self._max_title_length and len(win_info['title']) > self._max_title_length:
                    truncated_title = f"{win_info['title'][:self._max_title_length]}{self.max_title_ellipsis_fmt}"
                    win_info['title'] = truncated_title
                    self._window_title_text.setText(self._no_window_text)

                self._win_info = win_info
                self._update_text()

                if self._window_title_text.isHidden():
                    self._window_title_text.show()
        except Exception:
            print(traceback.format_exc())

    def _update_text(self):
        try:
            self._window_title_text.setText(self._active_label.format(win=self._win_info))
        except Exception:
            self._window_title_text.setText(self._active_label)
