import logging
from typing import Union
from settings import APP_BAR_TITLE
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt, QRect
from core.utils.utilities import is_valid_percentage_str, percent_to_float
from core.validation.bar import BAR_DEFAULTS


try:
    from core.utils.win32 import app_bar
    IMPORT_APP_BAR_MANAGER_SUCCESSFUL = True
except ImportError:
    IMPORT_APP_BAR_MANAGER_SUCCESSFUL = False


class Bar(QWidget):
    def __init__(
            self,
            bar_id: str,
            bar_name: str,
            bar_screen: QScreen,
            stylesheet: str,
            widgets: dict[str, list],
            class_name: str = BAR_DEFAULTS['class_name'],
            alignment: dict = BAR_DEFAULTS['alignment'],
            window_flags: dict = BAR_DEFAULTS['window_flags'],
            dimensions: dict = BAR_DEFAULTS['dimensions'],
            padding: dict = BAR_DEFAULTS['padding']
    ):
        super().__init__()
        self.hide()
        self.setScreen(bar_screen)

        self._bar_id = bar_id
        self._bar_name = bar_name
        self._alignment = alignment
        self._window_flags = window_flags
        self._dimensions = dimensions
        self._padding = padding

        self.screen_name = self.screen().name()
        self.app_bar_edge = app_bar.AppBarEdge.Top \
            if self._alignment['position'] == "top" \
            else app_bar.AppBarEdge.Bottom

        if self._window_flags['windows_app_bar'] and IMPORT_APP_BAR_MANAGER_SUCCESSFUL:
            self.app_bar_manager = app_bar.Win32AppBar()
        else:
            self.app_bar_manager = None

        self.setWindowTitle(APP_BAR_TITLE)
        self.setStyleSheet(stylesheet)
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        if self._window_flags['always_on_top']:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self._bar_frame = QFrame(self)
        self._bar_frame.setProperty("class", f"bar {class_name}")
        self._add_widgets(widgets)

        self.position_bar(init=True)
        self.try_add_app_bar()
        self.screen().geometryChanged.connect(self.on_screen_change, Qt.ConnectionType.QueuedConnection)
        self.show()

    @property
    def bar_id(self) -> str:
        return self._bar_id

    def on_screen_change(self, geo: QRect) -> None:
        logging.info(f"{self.bar_id} - screen geometry changed to {geo} (x{self.screen().devicePixelRatio()})")
        self.position_bar()
        self.try_add_app_bar()

    def try_add_app_bar(self) -> None:
        if self.app_bar_manager:
            self.app_bar_manager.create_appbar(
                self.winId().__int__(),
                self.app_bar_edge,
                self.native_bar_height(),
                self.screen()
            )

    def try_remove_app_bar(self) -> None:
        if self.app_bar_manager:
            self.app_bar_manager.remove_appbar()

    def native_bar_height(self) -> int:
        pixel_ratio = self.screen().devicePixelRatio()
        return int((self._padding['top'] + self._dimensions['height'] + self._padding['bottom']) * pixel_ratio)

    def position_bar(self, init=False) -> None:
        v_padding = self._padding['left'] + self._padding['right']
        h_padding = self._padding['top'] + self._padding['bottom']
        bar_w = self._calc_bar_width(self._dimensions['width'])
        bar_w = int(bar_w / self.screen().devicePixelRatio()) if init else bar_w
        bar_h = self._dimensions['height'] + h_padding
        bar_x, bar_y = self._calc_bar_pos(self._padding['left'], bar_w, bar_h)

        self.setGeometry(bar_x, bar_y, bar_w, bar_h)
        self._bar_frame.setGeometry(0, self._padding['top'], bar_w - h_padding, bar_h - v_padding)

    def _calc_bar_width(self, width: Union[str, int]) -> int:
        if is_valid_percentage_str(str(width)):
            return int(self.screen().geometry().width() * percent_to_float(width))
        else:
            return width

    def _calc_bar_pos(self, x_padding: int, bar_w: int, bar_h: int) -> tuple[int, int]:
        screen_x = self.screen().geometry().x()
        screen_y = self.screen().geometry().y()
        screen_w = self.screen().geometry().width()
        screen_h = self.screen().geometry().height()

        x = screen_x + (screen_w / 2) - int(bar_w / 2) if self._alignment['center'] else screen_x + x_padding
        y = screen_y + screen_h - bar_h if self._alignment['position'] == "bottom" else screen_y

        return int(x), int(y)

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
                widget.setFixedHeight(self._bar_frame.geometry().height())
                widget.parent_layout_type = layout_type
                widget.bar_id = self.bar_id
                layout.addWidget(widget, 0)

            if layout_type in ["left", "center"]:
                layout.addStretch()

            layout_container.setLayout(layout)
            bar_layout.addWidget(layout_container, 0, column_num)

        self._bar_frame.setLayout(bar_layout)
