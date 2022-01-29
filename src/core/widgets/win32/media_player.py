import asyncio
from core.widgets.base import BaseWidget
# from core.validation.widgets.example import EXAMPLE_VALIDATION_SCHEMA
from core.utils.win32 import media_control
from PyQt6.QtWidgets import QLabel


class MediaPlayerWidget(BaseWidget):
    validation_schema = {}

    def __init__(
            self,
            label: str = "t",
            label_alt: str = "1",
            update_interval: int = 1000,
            callbacks: dict[str, str] = {
                "on_left": "update_label",
                "on_middle": "update_label",
                "on_right": "update_label"
            }
    ):
        super().__init__(update_interval, class_name="template-widget")
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)
        self.register_callback("update_label", self._update_label)
        self.register_callback("toggle_label", self._toggle_label)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
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
        print("yeng")
        media_info = asyncio.run(media_control.get_media_info())
        print(media_info)
        # Update the active label at each timer interval
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label.setText(active_label_content)
