import logging
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMenu, QPushButton, QListView, QWidgetAction
from PyQt6.QtGui import QAction
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.dropdown import VALIDATION_SCHEMA

class DropdownWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            items: dict[str, str],
            update_interval: int,
            callbacks: dict[str, str]
    ):
        super().__init__(update_interval, class_name="dropdown-widget")
        
        self._items = items
        self._button = QPushButton("\udb83\ude6f")
        self._menu = QMenu(self._button)
        self._populate_menu()
        self._button.setMenu(self._menu)
        self.widget_layout.addWidget(self._button)
        
        self.register_callback("update_items", self._update_items)
        
        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_items"

        self.start_timer()

    def _populate_menu(self):
        for name, widget_name in self._items.items():
            widget_instance = self._create_widget_instance(widget_name)
            widget_action = QWidgetAction(self._menu)
            widget_action.setDefaultWidget(widget_instance)
            self._menu.addAction(widget_action)

    def _create_widget_instance(self, widget_name):
        # Correct import paths based on your project structure
        if widget_name == "cpu":
            from core.widgets.yasb.cpu import CpuWidget
            return CpuWidget(
                label="\ue266 CPU:{info[percent][total]}%",
                label_alt="CPU:{info[histograms][cpu_percent]}",
                histogram_icons=[
                    '\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588'
                ],
                histogram_num_columns=20,
                update_interval=1000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "memory":
            from core.widgets.yasb.memory import MemoryWidget
            return MemoryWidget(
                label="\ue266 RAM:{virtual_mem_percent}%",
                label_alt="\ue266 RAM:{virtual_mem_free}",
                update_interval=2000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd /c Taskmgr'
                },
                memory_thresholds={
                    'low': 25,
                    'medium': 50,
                    'high': 90
                }
            )
        elif widget_name == "volume":
            from core.widgets.yasb.volume import VolumeWidget
            return VolumeWidget(
                label="\uf028 {volume[percent]}",
                label_alt="\uf028 {volume[percent]}",
                update_interval=500,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:network'
                }
            )
        else:
            raise ValueError(f"Unknown widget: {widget_name}")

    def _update_items(self):
        try:
            self._menu.clear()
            self._populate_menu()
        except Exception:
            logging.exception("Failed to update dropdown items")
