import traceback
import psutil
from collections import deque
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.cpu import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel


# TODO : Add CPU temperature format options


class CpuWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            histogram_icons: list[str],
            histogram_num_columns: int,
            update_interval: int,
            callbacks: dict[str, str]
    ):
        super().__init__(update_interval, class_name="cpu-widget")
        self._histogram_icons = histogram_icons
        self._cpu_freq_history = deque([0] * histogram_num_columns, maxlen=histogram_num_columns)
        self._cpu_perc_history = deque([0] * histogram_num_columns, maxlen=histogram_num_columns)

        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._active_label = label
        self._label_text = QLabel()
        self._label_text.setProperty("class", "label")
        self.widget_layout.addWidget(self._label_text)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_label"

        self.start_timer()

    def _toggle_label(self):
        self._show_alt = not self._show_alt
        self._active_label = self._label_alt if self._show_alt else self._label
        self._update_label()

    def _get_histogram_bar(self, num, num_min, num_max):
        bar_index = int((num - num_min) / (num_max - num_min) * 10)
        bar_index = 8 if bar_index > 8 else bar_index
        return self._histogram_icons[bar_index]

    def _get_cpu_info(self) -> dict:
        cpu_freq = psutil.cpu_freq()
        cpu_stats = psutil.cpu_stats()
        min_freq = cpu_freq.min
        max_freq = cpu_freq.max
        current_freq = cpu_freq.current
        current_perc = psutil.cpu_percent()
        cores_perc = psutil.cpu_percent(percpu=True)

        self._cpu_freq_history.append(current_freq)
        self._cpu_perc_history.append(current_perc)

        return {
            'cores': {
                'physical': psutil.cpu_count(logical=False),
                'total': psutil.cpu_count(logical=True)
            },
            'freq': {
                'min': min_freq,
                'max': max_freq,
                'current': current_freq
            },
            'percent': {
                'core': cores_perc,
                'total': current_perc
            },
            'stats': {
                'context_switches': cpu_stats.ctx_switches,
                'interrupts': cpu_stats.interrupts,
                'soft_interrupts': cpu_stats.soft_interrupts,
                'sys_calls': cpu_stats.syscalls
            },
            'histograms': {
                'cpu_freq': "".join([
                    self._get_histogram_bar(freq, min_freq, max_freq) for freq in self._cpu_freq_history
                ]).encode('utf-8').decode('unicode_escape'),
                'cpu_percent': "".join([
                    self._get_histogram_bar(percent, 0, 100) for percent in self._cpu_perc_history
                ]).encode('utf-8').decode('unicode_escape'),
                'cores': "".join([
                    self._get_histogram_bar(percent, 0, 100) for percent in cores_perc
                ]).encode('utf-8').decode('unicode_escape'),
            }
        }

    def _update_label(self):
        try:
            info = self._get_cpu_info()
            self._label_text.setText(self._active_label.format(info=info))
        except Exception:
            self._label_text.setText(self._active_label)
            print(traceback.format_exc())
