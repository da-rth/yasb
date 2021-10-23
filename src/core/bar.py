from typing import Union, NewType, TypedDict, Literal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt

BarWidth = NewType('BarWidth', Union[str, int])
BarOffset = TypedDict('BarOffset', {'x': int, 'y': int})
BarPosition = Literal["TOP", "BOTTOM"]

BAR_POSITION_TOP: BarPosition = "TOP"
BAR_POSITION_BOTTOM: BarPosition = "BOTTOM"


class Bar(QWidget):

    def __init__(
            self,
            modules: dict[str, list] = None,
            screen: QScreen = None,
            position: BarPosition = "TOP",
            x_offset: int = 0,
            y_offset: int = 0,
            width: BarWidth = "100%",
            height: int = 30,
            centered: bool = False,
            stylesheet: str = None,
            hide_empty_module_containers: bool = False,
            always_on_top: bool = False,
            class_name=""
    ):
        super().__init__()
        self.hide()

        if screen:
            self.setScreen(screen)

        self.bar_is_centered = centered
        self.bar_position = position
        self.hide_empty_module_containers = hide_empty_module_containers
        self.bar = QFrame(self)
        self.bar.className = class_name
        self.bar.setProperty("class", f"bar {class_name}")

        self.setStyleSheet(stylesheet)

        self._set_window_attributes(always_on_top)
        self._set_geometry(x_offset, y_offset, width, height)
        self._add_modules(modules)

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
                layout.addWidget(widget, 0)

            if layout_type in ["left", "center"]:
                layout.addStretch()

            layout_container.setLayout(layout)

            bar_layout.addWidget(layout_container, 0, column_num)

        self.bar.setLayout(bar_layout)

    def _set_geometry(
            self,
            x_offset: int,
            y_offset: int,
            width: Union[int, str],
            height: int
    ):
        native_res_width = self._calc_bar_width(width)
        native_res_height = self._calc_bar_height(height)

        x, y = self._calc_adjusted_bar_offset(x_offset, y_offset, native_res_width, native_res_height)
        width = self._adjust_pixels_to_ratio(native_res_width)
        height = self._adjust_pixels_to_ratio(native_res_height)

        self.setGeometry(x, y, width, height)
        self.bar.setGeometry(0, 0, width, height)

    def _set_window_attributes(self, always_on_top: bool):
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def _calc_bar_width(self, width: BarWidth) -> int:

        def percent_to_float(percent: str) -> float:
            return float(percent.strip('%')) / 100.0

        def is_valid_percentage_str(s: str) -> bool:
            return s.endswith("%") and len(s) <= 4 and s[:-1].isdigit()

        bar_width = self.screen().geometry().width()

        if width:
            if isinstance(width, str) and is_valid_percentage_str(width):
                bar_width = self.screen().geometry().width() * percent_to_float(width)
            else:
                bar_width = abs(width)
        else:
            print("Failed to calculate bar width. Defaulting to full width.")

        return bar_width

    def _calc_bar_height(self, height: int) -> int:
        return abs(height)

    def _calc_adjusted_bar_offset(
            self,
            x_offset: int,
            y_offset: int,
            bar_width: int,
            bar_height: int
    ) -> tuple[int, int]:
        geo = self.screen().geometry()

        if self.bar_is_centered:
            center = (self.screen().geometry().width()) / 2
            x = geo.x() + self._adjust_pixels_to_ratio(center - int(bar_width / 2))
        else:
            x = self._adjust_pixels_to_ratio(geo.x() + x_offset)

        if self.bar_position == BAR_POSITION_TOP:
            y = self._adjust_pixels_to_ratio(geo.y() + y_offset)
        else:
            y = self._adjust_pixels_to_ratio(geo.height() - y_offset - bar_height)

        return x, y

    def _adjust_pixels_to_ratio(self, pixels: int) -> int:
        return pixels  # / self.screen().devicePixelRatio()
