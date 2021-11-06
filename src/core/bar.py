from typing import Union
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt
from core.utils.utilities import is_valid_percentage_str, percent_to_float
from core.validation.bar import BAR_DEFAULTS

try:
    from core.utils.win32.app_bar import Win32AppBar, AppBarEdge
    IMPORT_APP_BAR_MANAGER_SUCCESSFUL = True
except ImportError:
    IMPORT_APP_BAR_MANAGER_SUCCESSFUL = False

BAR_WM_TITLE = "YasbBar"


class Bar(QWidget):
    def __init__(
            self,
            bar_index: int,
            bar_name: str,
            bar_screen: QScreen = None,
            stylesheet: str = "",
            class_name: str = BAR_DEFAULTS['class_name'],
            alignment: dict = BAR_DEFAULTS['alignment'],
            window_flags: dict = BAR_DEFAULTS['window_flags'],
            dimensions: dict = BAR_DEFAULTS['dimensions'],
            offset: dict = BAR_DEFAULTS['offset'],
            widgets: list[QWidget] = BAR_DEFAULTS['widgets']
    ):
        super().__init__()
        self.hide()
        self._bar_index = bar_index
        self._bar_name = bar_name
        self._alignment = alignment
        self._window_flags = window_flags
        self._dimensions = dimensions
        self._offset = offset

        if bar_screen:
            self.setScreen(bar_screen)

        self.setWindowTitle(BAR_WM_TITLE)
        self.setStyleSheet(stylesheet)
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if self._window_flags['always_on_top']:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self._bar_frame = QFrame(self)
        self._bar_frame.setProperty("class", f"bar {class_name}")

        bar_width = self._calc_bar_width(self._dimensions['width'])
        bar_height = self._dimensions['height']
        bar_x, bar_y = self._calc_adjusted_bar_offset(self._offset['x'], self._offset['y'], bar_width, bar_height)
        self.setGeometry(bar_x, bar_y, bar_width, bar_height)
        self._bar_frame.setGeometry(0, 0, bar_width, bar_height)

        if self._window_flags['windows_app_bar'] and IMPORT_APP_BAR_MANAGER_SUCCESSFUL:
            self.appbar_edge = AppBarEdge.Top if self._alignment['position'] == "top" else AppBarEdge.Bottom
            self.app_bar_manager = Win32AppBar(self, self.appbar_edge)
            self.app_bar_manager.create_appbar()
        else:
            self.appbar_edge = None
            self.app_bar_manager = None

        self._add_widgets(widgets)

    def _calc_bar_width(self, width: Union[str, int]) -> int:
        if isinstance(width, str) and is_valid_percentage_str(width):
            return int(self.screen().geometry().width() * percent_to_float(width))
        return width

    def _calc_adjusted_bar_offset(self, x_offset: int, y_offset: int, bar_w: int, bar_h: int) -> tuple[int, int]:
        geo = self.screen().geometry()

        if self._alignment['center']:
            x = int(geo.x() + (geo.width() / 2) - int(bar_w / 2))
        else:
            x = geo.x() + x_offset

        if self._alignment['position'] == "bottom":
            y = geo.height() - y_offset - bar_h
        else:
            y = geo.y() + y_offset

        return x, y

    def _add_widgets(self, widgets: dict[str, list] = None):
        bar_layout = QGridLayout()
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        for column_num, layout_type in enumerate(['left', 'center', 'right']):
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            layout_container = QFrame()
            layout_container.setProperty("class", f"container container-{layout_type}")

            if layout_type in ["center", "right"]:
                layout.addStretch()

            for widget in widgets[layout_type]:
                widget.setFixedHeight(self._bar_frame.geometry().height() - 2)
                widget.parent_layout_type = layout_type
                widget.bar_index = self._bar_index
                layout.addWidget(widget, 0)

            if layout_type in ["left", "center"]:
                layout.addStretch()

            layout_container.setLayout(layout)

            bar_layout.addWidget(layout_container, 0, column_num)

        self._bar_frame.setLayout(bar_layout)
