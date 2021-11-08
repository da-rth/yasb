import traceback
import psutil
from humanize import naturalsize
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.memory import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel


class MemoryWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            update_interval: int,
            callbacks: dict[str, str],
            memory_thresholds: dict[str, int]
    ):
        super().__init__(update_interval, class_name="memory-widget")
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._active_label = label
        self._mem_text = QLabel()
        self._mem_text.setProperty("class", "label")
        self.widget_layout.addWidget(self._mem_text)

        self.register_callback("toggle_label", self._toggle_memory_info)
        self.register_callback("update_memory_info", self._update_memory_info)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_memory_info"

        self._percent_thresholds = memory_thresholds

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
            self._mem_text.setProperty("class", f"label status-{threshold}")
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
