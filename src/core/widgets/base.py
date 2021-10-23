from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import QTimer, Qt
from typing import Union
import subprocess


class BaseWidget(QWidget):

    def __init__(
            self,
            timer_interval: int = None,
            class_name: str = ""
    ):
        super().__init__()
        self.timer_interval = timer_interval
        self.className = class_name
        self.setProperty("class", f"widget {class_name}")
        self.timer = QTimer(self)
        self.mousePressEvent = self._handle_mouse_events

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.callbacks = dict()
        self.register_callback("default", self._cb_do_nothing)
        self.register_callback("do_nothing", self._cb_do_nothing)
        self.register_callback("exec", self._cb_execute_subprocess)

        self.callback_default: Union[str, list[str]] = "default"
        self.callback_timer: Union[str, list[str]] = "default"
        self.callback_left: Union[str, list[str]] = self.callback_default
        self.callback_middle: Union[str, list[str]] = self.callback_default
        self.callback_right: Union[str, list[str]] = self.callback_default

    def register_callback(self, callback_name, fn):
        self.callbacks[callback_name] = fn

    def start_timer(self):
        if self.timer_interval and self.timer_interval > 0:
            self.timer.timeout.connect(self._timer_callback)
            self.timer.start(self.timer_interval)
        self._timer_callback()

    def _handle_mouse_events(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._run_callback(self.callback_left)
        elif event.button() == Qt.MouseButton.MiddleButton:
            self._run_callback(self.callback_middle)
        elif event.button() == Qt.MouseButton.RightButton:
            self._run_callback(self.callback_right)

    def _run_callback(self, cb: Union[str, list]):
        is_cb_list = isinstance(cb, list)
        cb_name = cb[0] if is_cb_list else cb
        cb_args = cb[1:] if is_cb_list else []
        is_valid_callback = cb_name in self.callbacks.keys()
        self.callback = self.callbacks[cb_name if is_valid_callback else 'default']

        try:
            self.callbacks[cb_name](*cb_args)
        except Exception as e:
            print(f"Failed to execute callback {cb_name} with args {cb_args}", e)

    def _timer_callback(self):
        self._run_callback(self.callback_timer)

    def _cb_execute_subprocess(self, cmd: str, cmd_args: str = None):
        subprocess.Popen([cmd, cmd_args] if cmd_args else [cmd])

    def _cb_do_nothing(self):
        pass
