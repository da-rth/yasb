from datetime import datetime
from .base import BaseWidget
from PyQt6.QtWidgets import QLabel
from tzlocal import get_localzone_name
from itertools import cycle
from typing import Union
import pytz


class ClockWidget(BaseWidget):

    def __init__(
            self,
            interval: int = 1000,
            class_name: str = "",
            label: str = "{datetime}",
            label_alt: str = "{datetime}",
            clock_fmt: str = "%H:%M:%S",
            clock_fmt_alt: str = "%d-%m-%y %H:%M:%S",
            on_left: Union[str, list[str]] = "toggle_clock_text",
            on_middle: Union[str, list[str]] = "do_nothing",
            on_right: Union[str, list[str]] = "next_timezone",
            timezones=None,
    ):
        super().__init__(interval, class_name)
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._clock_fmt = clock_fmt
        self._clock_fmt_alt = clock_fmt_alt
        self._active_tz = None
        self._active_label = label
        self._active_clock_fmt = clock_fmt
        self._timezones = cycle(timezones if timezones else [get_localzone_name()])

        self._clock_text = QLabel()
        self._clock_text.setProperty("class", f"clock-widget {class_name}")
        self.layout.addWidget(self._clock_text)

        self.register_callback("toggle_clock_text", self.toggle_clock_text)
        self.register_callback("update_clock_text", self.update_clock_text)
        self.register_callback("next_timezone", self.next_timezone)

        self.callback_left = on_left
        self.callback_right = on_right
        self.callback_middle = on_middle
        self.callback_timer = "update_clock_text"

        self.next_timezone()
        self.start_timer()

    def toggle_clock_text(self):
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        self._active_clock_fmt = self._clock_fmt_alt if self._show_alt else self._clock_fmt
        self.update_clock_text()

    def next_timezone(self):
        self._active_tz = next(self._timezones)
        self.setToolTip(self._active_tz)
        self.update_clock_text()

    def update_clock_text(self):
        try:
            dt_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(self._active_tz))
            self._clock_text.setText(self._active_label.format(datetime=dt_now.strftime(self._active_clock_fmt)))
        except Exception as e:
            print(e)
            self._clock_text.setText(self._active_label)
