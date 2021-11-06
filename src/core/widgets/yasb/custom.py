import subprocess
import json
from PyQt6.QtWidgets import QLabel
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.custom import VALIDATION_SCHEMA


class CustomWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            label_max_length: int,
            exec_options: dict,
            callbacks: dict,
            class_name: str
    ):
        super().__init__(exec_options.get('run_interval', 0), class_name="custom-widget")
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt if label_alt else label
        self._label_max_length = label_max_length

        self.register_callback("toggle", self.toggle)
        self.register_callback("exec_custom", self._exec_callback)
        self._custom_text = QLabel()

        self._exec_data = None
        self._exec_cmd = exec_options['run_cmd']
        self._exec_return_type = exec_options['return_format']
        self._exec_return_encoding = exec_options['return_encoding']
        self._exec_run_once = exec_options['run_once']

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "exec_custom"

        if class_name:
            self._custom_text.setProperty("class", f"custom-widget {class_name}")

        if not self._exec_cmd:
            self._custom_text.setText(label)

        self.widget_layout.addWidget(self._custom_text)

        if self._exec_run_once:
            self._exec_callback()
        else:
            self.start_timer()

    def toggle(self):
        self._show_alt = not self._show_alt
        self._update_label()

    def _exec_callback(self):
        self._exec_data = None

        if self._exec_cmd:
            proc = subprocess.Popen(self._exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            output = proc.stdout.read()

            if self._exec_return_type == "json":
                self._exec_data = json.loads(output)
            else:
                self._exec_data = output.decode(self._exec_return_encoding).strip()

            self._update_label()

    def _truncate_label(self, label):
        if self._label_max_length and len(label) > self._label_max_length:
            return label[:self._label_max_length] + "..."
        else:
            return label

    def _update_label(self):
        active_label = self._label_alt if self._show_alt else self._label

        try:
            label = active_label.format(data=self._exec_data)
        except Exception:
            label = active_label

        self._custom_text.setText(self._truncate_label(label))
