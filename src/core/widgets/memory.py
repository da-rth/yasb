import traceback
import psutil
from humanize import naturalsize
from core.widgets.base import BaseWidget
from core.utils.win32.utilities import open_task_manager
from PyQt6.QtWidgets import QLabel
from typing import Union


class MemoryWidget(BaseWidget):

    def __init__(
            self,
            interval: int = 500,
            label: str = "\uf538  {virtual_mem_free}/{virtual_mem_total}",
            label_alt: str = "\uf538  VIRT: {virtual_mem_percent}% SWAP: {swap_mem_percent}%",
            on_left: Union[str, list[str]] = "toggle_memory_info",
            on_middle: Union[str, list[str]] = "toggle_memory_info",
            on_right: Union[str, list[str]] = "open_task_manager",
            percent_threshold_low: int = 25,
            percent_threshold_medium: int = 50,
            percent_threshold_high: int = 90
    ):
        super().__init__(interval, class_name="memory-widget")
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._active_label = label
        self._mem_text = QLabel()
        self._mem_text.setProperty("class", "memory-label")
        self.widget_layout.addWidget(self._mem_text)

        self.register_callback("toggle_memory_info", self._toggle_memory_info)
        self.register_callback("update_memory_info", self._update_memory_info)
        self.register_callback("open_task_manager", open_task_manager)

        self.callback_left = on_left
        self.callback_right = on_right
        self.callback_middle = on_middle
        self.callback_timer = "update_memory_info"

        self._percent_thresholds = {
            'low': percent_threshold_low,
            'medium': percent_threshold_medium,
            'high': percent_threshold_high
        }

        self.start_timer()

    def _toggle_memory_info(self):
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        self._update_memory_info()

    def _update_memory_info(self):
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            mem_text = self._active_label
            threshold = self._get_virtual_memory_threshold(virtual_mem.percent)
            label_options = [
                ("{virtual_mem_free}", naturalsize(virtual_mem.free)),
                ("{virtual_mem_percent}", virtual_mem.percent),
                ("{virtual_mem_total}", naturalsize(virtual_mem.total)),
                ("{virtual_mem_avail}", naturalsize(virtual_mem.available)),
                ("{swap_mem_free}", naturalsize(swap_mem.free)),
                ("{swap_mem_percent}", swap_mem.percent),
                ("{swap_mem_total}", naturalsize(swap_mem.total)),
            ]

            for fmt_str, value in label_options:
                mem_text = mem_text.replace(fmt_str, str(value))

            self._mem_text.setText(mem_text)
            self._mem_text.setProperty("class", f"battery-label status-{threshold}")
            self._mem_text.setStyleSheet('')
        except Exception:
            print(traceback.format_exc())

    def _get_virtual_memory_threshold(self, virtual_memory_percent) -> str:
        if virtual_memory_percent <= self._percent_thresholds['low']:
            return "low"
        elif self._percent_thresholds['low'] < virtual_memory_percent <= self._percent_thresholds['medium']:
            return "medium"
        elif self._percent_thresholds['medium'] < virtual_memory_percent <= self._percent_thresholds['high']:
            return "high"
        elif self._percent_thresholds['high'] < virtual_memory_percent:
            return "critical"
