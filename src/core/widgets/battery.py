from datetime import timedelta
from .base import BaseWidget
from PyQt6.QtWidgets import QLabel
from typing import Union, Literal
import psutil
import humanize


BatteryIconPosition = Literal["left", "right"]


class BatteryWidget(BaseWidget):

    def __init__(
            self,
            # Battery status updates every 2 seconds by default
            interval: int = 2000,
            # label variable options: {icon}, {percent}, {time_remaining}, {is_charging}
            label: str = "{icon}",
            label_alt: str = "{percent}% | remaining: {time_remaining}",
            # Battery status changes when percent <= threshold
            percent_threshold_critical: int = 10,
            percent_threshold_low: int = 25,
            percent_threshold_medium: int = 75,
            percent_threshold_high: int = 95,
            percent_threshold_full: int = 100,
            # FontAwesome Icons: https://fontawesome.com/v5.15/how-to-use/on-the-desktop/setup/getting-started
            icon_charging_blink: bool = True,
            icon_charging_format: str = "{charging_icon}  {icon}",
            icon_charging: str = "\uf0e7",
            icon_critical: str = "\uf244",
            icon_low: str = "\uf243",
            icon_medium: str = "\uf242",
            icon_high: str = "\uf241",
            icon_full: str = "\uf240",
            # Displays timestamp in natural language form
            natural_timestamp: bool = True,
            on_left: Union[str, list[str]] = "toggle_label",
            on_middle: Union[str, list[str]] = "toggle_label",
            on_right: Union[str, list[str]] = "toggle_label",
    ):
        super().__init__(interval, class_name="battery-widget")
        self._battery_state = None
        self._blink = False
        self._show_alt = False
        self._last_threshold = None
        self._icon_charging_format = icon_charging_format
        self._icon_charging_blink = icon_charging_blink
        self._label = label
        self._label_alt = label_alt
        self._active_label = label
        self._natural_timestamp = natural_timestamp
        self._percent_thresholds = {
            'critical': percent_threshold_critical,
            'low': percent_threshold_low,
            'medium': percent_threshold_medium,
            'high': percent_threshold_high,
            'full': percent_threshold_full
        }
        self._battery_icons = {
            'charging': icon_charging,
            'critical': icon_critical,
            'low': icon_low,
            'medium': icon_medium,
            'high': icon_high,
            'full': icon_full
        }

        self.register_callback("update_battery_info", self.update_battery_info)
        self.register_callback("toggle_label", self.toggle_label)

        self.callback_left = on_left
        self.callback_right = on_right
        self.callback_middle = on_middle
        self.callback_timer = "update_battery_info"

        self._battery_label = QLabel()
        self._battery_label.setProperty("class", "battery-label")
        self.widget_layout.addWidget(self._battery_label)
        self.start_timer()

    def update_battery_info(self):
        self._battery_state = psutil.sensors_battery()
        self._update_charging_label()

    def toggle_label(self):
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        self.update_battery_info()

    def _get_time_remaining(self) -> str:
        secs_left = self._battery_state.secsleft

        if secs_left == psutil.POWER_TIME_UNLIMITED:
            time_left = "unlimited"
        elif type(secs_left) == int:
            time_left = timedelta(seconds=secs_left)
            time_left = humanize.naturaldelta(time_left) if self._natural_timestamp else str(time_left)
        else:
            time_left = "unknown"

        return time_left

    def _get_battery_threshold(self):
        percent = self._battery_state.percent

        if percent <= self._percent_thresholds['critical']:
            return "critical"
        elif self._percent_thresholds['critical'] < percent <= self._percent_thresholds['low']:
            return "low"
        elif self._percent_thresholds['low'] < percent <= self._percent_thresholds['medium']:
            return "medium"
        elif self._percent_thresholds['medium'] < percent <= self._percent_thresholds['high']:
            return "high"
        elif self._percent_thresholds['high'] < percent <= self._percent_thresholds['full']:
            return "full"

    def _get_charging_icon(self, threshold: str):
        if self._battery_state.power_plugged:
            if self._icon_charging_blink and self._blink:
                empty_charging_icon = len(self._battery_icons["charging"]) * " "
                icon_str = self._icon_charging_format \
                    .replace("{charging_icon}", empty_charging_icon) \
                    .replace("{icon}", self._battery_icons[threshold])
                self._blink = not self._blink
            else:
                icon_str = self._icon_charging_format\
                    .replace("{charging_icon}", self._battery_icons["charging"])\
                    .replace("{icon}", self._battery_icons[threshold])

            return icon_str
        else:
            return self._battery_icons[threshold]

    def _update_charging_label(self):
        threshold = self._get_battery_threshold()
        time_remaining = self._get_time_remaining()
        is_charging_str = "yes" if self._battery_state.power_plugged else "no"
        charging_icon = self._get_charging_icon(threshold)
        battery_status = self._active_label\
            .replace("{percent}", str(self._battery_state.percent)) \
            .replace("{time_remaining}", time_remaining) \
            .replace("{is_charging}", is_charging_str) \
            .replace("{icon}", charging_icon)

        if self._battery_state.power_plugged:
            threshold = "charging"

        self._battery_label.setText(battery_status)
        self._battery_label.setProperty("class", f"battery-label status-{threshold}")
        self._battery_label.setStyleSheet(self.styleSheet())
