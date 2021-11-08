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
            icon: dict,
            exec_options: dict,
            callbacks: dict,
            class_name: str
    ):
        super().__init__(exec_options['run_interval'], class_name=f"custom-widget {class_name}")
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt if label_alt else label
        self._label_max_length = label_max_length

        self.register_callback("toggle_label", self.toggle)
        self.register_callback("exec_custom", self._exec_callback)
        self._exec_data = None
        self._exec_cmd = exec_options['run_cmd']

        if self._exec_cmd:
            self._exec_cmd = self._exec_cmd.split(" ")

        self._exec_return_type = exec_options['return_format']

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "exec_custom"

        if class_name:
            self.widget_layout.setProperty("class", class_name)

        self._custom_text = QLabel()
        self._custom_text.setProperty("class",  "label")
        self._custom_text.setText(label)

        if icon and icon['label']:
            self._icon_text = QLabel()
            self._icon_text.setText(icon['label'])
            self._icon_text.setProperty("class", f"icon icon-{icon['position']}")

            if icon['position'] == 'left':
                self.widget_layout.addWidget(self._icon_text)
                self.widget_layout.addWidget(self._custom_text)
            else:
                self.widget_layout.addWidget(self._custom_text)
                self.widget_layout.addWidget(self._icon_text)
        else:
            self.widget_layout.addWidget(self._custom_text)

        if exec_options['run_once']:
            self._exec_callback()
        else:
            self.start_timer()

    def toggle(self):
        self._show_alt = not self._show_alt
        self._update_label()

    def _exec_callback(self):
        self._exec_data = None

        if self._exec_cmd:
            # TODO: Log stderr if present
            proc = subprocess.Popen(self._exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            output = proc.stdout.read()

            if self._exec_return_type == "json":
                self._exec_data = json.loads(output)
            else:
                self._exec_data = output.decode('utf-8').strip()

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

    def _cb_execute_subprocess(self, cmd: str, *cmd_args: list[str]):
        # Overrides 'exec' callback to allow for data formatting
        if self._exec_data:
            formatted_cmd_args = []
            for cmd_arg in cmd_args:
                try:
                    formatted_cmd_args.append(cmd_arg.format(data=self._exec_data))
                except KeyError:
                    formatted_cmd_args.append(cmd_args)
            cmd_args = formatted_cmd_args
        subprocess.Popen([cmd, *cmd_args] if cmd_args else [cmd])
