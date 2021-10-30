from typing import Union
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt
from cssutils.css import CSSStyleSheet
from enum import Enum
from core.utils.utilities import is_valid_percentage_str, percent_to_float

BAR_WM_TITLE = "YasbBar"


class Position(Enum):
    top = "top"
    bottom = "bottom"


class Bar(QWidget):

    def __init__(
            self,
            bar_index: int,
            modules: dict[str, list] = None,
            screen: QScreen = None,
            position: Position = None,
            x_offset: int = 0,
            y_offset: int = 0,
            width: Union[str, int] = "100%",
            height: int = 30,
            centered: bool = False,
            stylesheet: CSSStyleSheet = None,
            hide_empty_module_containers: bool = False,
            always_on_top: bool = False,
            class_name=""
    ):
        super().__init__()
        self.hide()

        if screen:
            self.setScreen(screen)

        self.setWindowTitle(BAR_WM_TITLE)
        self.bar_index = bar_index
        self.bar_is_centered = centered
        self.bar_position = position
        self.hide_empty_module_containers = hide_empty_module_containers
        self.bar = QFrame(self)
        self.bar.className = class_name
        self.bar.setProperty("class", f"bar {class_name}")

        self.setStyleSheet(stylesheet.cssText.decode("utf-8"))

        self._set_window_attributes(always_on_top)
        self._set_geometry(x_offset, y_offset, width, height)
        self._add_modules(modules)

    def _set_window_attributes(self, always_on_top: bool):
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def _set_geometry(
            self,
            x_offset: int,
            y_offset: int,
            width: Union[int, str],
            height: int
    ):
        width = self._calc_bar_width(width)
        x, y = self._calc_adjusted_bar_offset(x_offset, y_offset, width, height)
        self.setGeometry(x, y, width, height)
        self.bar.setGeometry(0, 0, width, height)

    def _calc_bar_width(self, width: Union[str, int]) -> int:
        if isinstance(width, str) and is_valid_percentage_str(width):
            return int(self.screen().geometry().width() * percent_to_float(width))
        else:
            return width

    def _calc_adjusted_bar_offset(self, x_offset: int, y_offset: int, bar_w: int, bar_h: int) -> tuple[int, int]:
        geo = self.screen().geometry()

        if self.bar_is_centered:
            x = int(geo.x() + (geo.width() / 2) - int(bar_w / 2))
        else:
            x = geo.x() + x_offset

        if self.bar_position == Position.bottom:
            y = geo.height() - y_offset - bar_h
        else:
            print("failed to match position bottom")
            y = geo.y() + y_offset

        return x, y

    def _add_modules(self, modules: dict[str, list] = None):
        bar_layout = QGridLayout()
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        for column_num, layout_type in enumerate(['left', 'center', 'right']):
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            layout_container = QFrame()
            layout_container.className = f"container container-{layout_type}"
            layout_container.setProperty("class", layout_container.className)

            if layout_type in ["center", "right"]:
                layout.addStretch()

            for widget in modules[layout_type]:
                widget.setFixedHeight(self.bar.geometry().height() - 2)
                widget.parent_layout_type = layout_type
                widget.bar_index = self.bar_index
                layout.addWidget(widget, 0)

            if layout_type in ["left", "center"]:
                layout.addStretch()

            layout_container.setLayout(layout)

            bar_layout.addWidget(layout_container, 0, column_num)

        self.bar.setLayout(bar_layout)
