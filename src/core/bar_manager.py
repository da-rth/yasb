from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from core.bar import Bar
from core.widgets.clock import ClockWidget
from core.widgets.custom import CustomWidget
from core.widgets.battery import BatteryWidget
from core.widgets.komorebi.workspaces import WorkspaceWidget
from .bar import BAR_POSITION_TOP, BAR_POSITION_BOTTOM
from cssutils.css import CSSStyleSheet


class BarManager(QWidget):

    def __init__(self):
        super().__init__()
        self.bars: list[Bar] = []
        self.setWindowFlags(Qt.WindowType.Tool)
        self.hide()

    def add_bar(self, screen, bar_config: dict, stylesheet: CSSStyleSheet):
        bar_position = BAR_POSITION_TOP if bar_config.get('position', "top") == "top" else BAR_POSITION_BOTTOM
        offset = bar_config.get('offset', {})

        # TODO Read modules from bar_config
        modules = self.build_bar_modules()

        bar = Bar(
            screen=screen,
            width=bar_config.get('width', '100%'),
            centered=bar_config.get('centered', False),
            position=bar_position,
            height=bar_config.get('height', 30),
            hide_empty_module_containers=True,
            x_offset=offset.get('x', 0),
            y_offset=offset.get('y', 0),
            class_name=bar_config.get('class_name', ''),
            stylesheet=stylesheet,
            modules=modules,
            always_on_top=bar_config.get('always_on_top', False)
        )

        self.bars.append(bar)

    def show_bars(self):
        for bar in self.bars:
            bar.show()

    def hide_bars(self):
        for bar in self.bars:
            bar.hide()

    def build_bar_modules(self):
        return {
            'left': [WorkspaceWidget()],
            'center': [ClockWidget()],
            'right': [
                CustomWidget(
                    class_name="terminal-widget",
                    label="\uf120",
                    label_alt="Open Windows Terminal",
                    on_left=["exec", "wt.exe"]
                ),
                CustomWidget(
                    class_name="explorer-widget",
                    label="\uf07c",
                    label_alt="Open Explorer",
                    on_left=["exec", "explorer.exe"]
                ),
                BatteryWidget(),
                CustomWidget(
                    class_name="hostname-widget",
                    label="{data}",
                    exec_run_once=True,
                    exec_cmd=["hostname"]
                )
            ]
        }
