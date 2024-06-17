from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.disk import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
import os


class DiskWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        volume_label: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="disk-widget")
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt
        self._volume_label = volume_label

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self._label.show()
        self._label_alt.hide()

        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()

        self._update_label()

    def _update_label(self):
        # Determine which label is active
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label.setText(active_label_content)

        # Format the label content
        try:
            disk_space = self._get_space()

            active_label.setText(active_label_content.format(space=disk_space, volume_label=self._volume_label))
        except Exception:
            active_label.setText(active_label_content)

    def _get_space(self):
        result = os.popen("WMIC LOGICALDISK GET Name,Size,FreeSpace").read() # WMIC is deprecated, but all other options require elevation
        for line in result.split("\n"):
            if self._volume_label in line:
                used_space = int(line.split()[0].strip())
                total_space = int(line.split()[2].strip())

        if used_space and total_space:
            return {
                "total": {
                    'mb': total_space / 1024,
                    'gb': total_space / 1024**3
                },
                "used": {
                    'mb': used_space / 1024,
                    'gb': used_space / 1024**3,
                    'percent': (used_space / total_space) * 100
                },
                "free": {
                    'mb': (total_space - used_space) / 1024,
                    'gb': (total_space / 1024**3) - (used_space / 1024**3),
                    'percent': ((total_space - used_space) / total_space) * 100
                }
            }