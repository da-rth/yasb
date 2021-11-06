import re
import pytz
from datetime import datetime
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.clock import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from tzlocal import get_localzone_name
from itertools import cycle


class ClockWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            update_interval: int,
            timezones: list[str],
            callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="clock-widget")
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._active_tz = None
        self._active_label = label
        self._timezones = cycle(timezones if timezones else [get_localzone_name()])
        self._clock_text = QLabel()
        self._clock_text.setProperty("class", "clock-label")
        self._active_datetime_format_str = ''
        self._active_datetime_format = None
        self.widget_layout.addWidget(self._clock_text)

        self.register_callback("toggle_label", self.toggle_clock_text)
        self.register_callback("update_clock_text", self.update_clock_text)
        self.register_callback("next_timezone", self.next_timezone)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_clock_text"

        self.next_timezone()
        self.update_timestamp_format()
        self.start_timer()

    def toggle_clock_text(self):
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        self.update_timestamp_format()
        self.update_clock_text()

    def update_timestamp_format(self):
        datetime_format_search = re.search('\{(.*)}', self._active_label)
        self._active_datetime_format_str = datetime_format_search.group()
        self._active_datetime_format = datetime_format_search.group(1)

    def next_timezone(self):
        self._active_tz = next(self._timezones)
        self.setToolTip(self._active_tz)
        self.update_clock_text()

    def update_clock_text(self):
        try:
            dt_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(self._active_tz))
            clock_text = self._active_label.replace(
                self._active_datetime_format_str,
                dt_now.strftime(self._active_datetime_format)
            )
            self._clock_text.setText(clock_text)
        except Exception:
            self._clock_text.setText(self._active_label)
