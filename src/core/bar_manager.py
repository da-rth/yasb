import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal
from cssutils.css import CSSStyleSheet
from core.bar import Bar, Position
from core.widgets.clock import ClockWidget
from core.widgets.custom import CustomWidget
from core.widgets.battery import BatteryWidget
from core.widgets.komorebi.workspaces import WorkspaceWidget
from core.widgets.active_window import ActiveWindowWidget
from core.event_service import EventService
from core.event_enums import BarEvent


class BarManager(QObject):
    close_bar_signal = pyqtSignal(int)
    reload_bars_signal = pyqtSignal()

    def __init__(self, app: QApplication, config: dict, stylesheet: CSSStyleSheet):
        super().__init__()
        self._app = app
        self._config = config
        self._stylesheet = stylesheet
        self._bars: list[Bar] = []
        self._event_service = EventService()
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_tasks = []
        self._register_signals_and_events()

    def _register_signals_and_events(self):
        self.close_bar_signal.connect(self._on_close_bar_event)
        self.reload_bars_signal.connect(self._on_reload_bars_event)

        self._event_service.register_event(BarEvent.CloseBar, self.close_bar_signal)
        self._event_service.register_event(BarEvent.ReloadBars, self.reload_bars_signal)

    def add_bar(self, screen, bar_config: dict, stylesheet: CSSStyleSheet):
        offset = bar_config.get('offset', {})
        bar_index = len(self._bars)

        try:
            bar_position = Position[bar_config.get('position', "bottom")]
        except KeyError:
            bar_position = Position.top

        bar = Bar(
            bar_index,
            screen=screen,
            enable_win32_appbar=True,
            width=bar_config.get('width', '100%'),
            centered=bar_config.get('centered', False),
            position=bar_position,
            height=bar_config.get('height', 30),
            hide_empty_module_containers=True,
            x_offset=offset.get('x', 0),
            y_offset=offset.get('y', 0),
            class_name=bar_config.get('class_name', ''),
            stylesheet=stylesheet,
            modules=self._build_bar_modules(),
            always_on_top=bar_config.get('always_on_top', False)
        )

        self._bars.append(bar)

    def num_bars(self):
        return len(self._bars)

    def add_background_task(self, func, *args):
        self._thread_tasks.append([func, *args])

    def run_background_tasks(self):
        for func, *args in self._thread_tasks:
            try:
                self._thread_pool.start(func, *args)
            except Exception:
                print(traceback.format_exc())

    def show_bars(self):
        for bar in self._bars:
            bar.show()

    def hide_bars(self):
        for bar in self._bars:
            bar.hide()

    def close_bars(self):
        for bar in self._bars:

            if bar.win32_app_bar:
                bar.win32_app_bar.remove_appbar()

            bar.close()

    def initialize_bars(self):
        self._bars = []

        for bar_config in self._config['bars']:
            if bar_config['screen'] == "all":
                for screen in self._app.screens():
                    print("Adding bar to", screen.name())
                    self.add_bar(screen, bar_config, self._stylesheet)
            else:
                screen_name = bar_config['screen']
                matched_screen = next(filter(lambda scr: screen_name in scr.name(), self._app.screens()), None)

                if matched_screen:
                    print("Adding bar to", matched_screen.name())
                    self.add_bar(matched_screen, bar_config, self._stylesheet)

    def _on_reload_bars_event(self):
        print("Reloading all bars")
        self.close_bars()
        self.initialize_bars()

    def _on_close_bar_event(self, bar_index: int):
        try:
            bar = self._bars[bar_index]

            if bar.win32_app_bar:
                bar.win32_app_bar.remove_appbar()

            bar.close()
            print("Closed bar", bar_index, "on screen", bar.scree.name())
        except IndexError:
            print("Failed to close bar with index", bar_index, "due to IndexError")

    def _build_bar_modules(self):
        return {
            'left': [
                WorkspaceWidget(),
                ActiveWindowWidget()
            ],
            'center': [
                ClockWidget(
                    # Open Clock App on right click
                    on_right=["exec", "explorer.exe", "shell:Appsfolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"]
                )
            ],
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
