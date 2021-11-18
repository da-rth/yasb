from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from cssutils.css import CSSStyleSheet
from core.bar import Bar
from core.utils.widget_builder import WidgetBuilder
from core.event_service import EventService
from core.event_enums import BarEvent
from copy import deepcopy


class BarManager(QObject):
    close_bar_signal = pyqtSignal(int)
    reload_bars_signal = pyqtSignal()

    def __init__(self, app: QApplication, config: dict, stylesheet: CSSStyleSheet):
        super().__init__()
        self.event_service = EventService()
        self.widget_event_listeners = set()
        self._app = app
        self._config = config
        self._stylesheet = stylesheet
        self._bars: list[Bar] = []
        self._register_signals_and_events()
        self._widget_builder: WidgetBuilder = None
        self._threads = {}

    def _register_signals_and_events(self):
        self.close_bar_signal.connect(self._on_close_bar_event)
        self.reload_bars_signal.connect(self._on_reload_bars_event)
        self.event_service.register_event(BarEvent.CloseBar, self.close_bar_signal)
        self.event_service.register_event(BarEvent.ReloadBars, self.reload_bars_signal)

    def add_bar(self, bar_options: dict):
        bar = Bar(**bar_options)
        self._bars.append(bar)

    def num_bars(self):
        return len(self._bars)

    def run_listeners_in_threads(self):
        for listener in self.widget_event_listeners:
            print("Activating listener", listener)
            thread = QThread()
            event_listener = listener()
            event_listener.moveToThread(thread)
            thread.started.connect(event_listener.start)
            thread.start()

            self._threads[listener] = thread

    def show_bars(self):
        for bar in self._bars:
            bar.show()

    def hide_bars(self):
        for bar in self._bars:
            bar.hide()

    def close_bars(self):
        for bar in self._bars:
            if bar.app_bar_manager:
                bar.app_bar_manager.remove_appbar()
            bar.close()

    def initialize_bars(self) -> None:
        self._widget_builder = WidgetBuilder(self._config['widgets'])

        for bar_index, (bar_name, bar_config) in enumerate(self._config['bars'].items()):

            if not bar_config['enabled']:
                continue

            if '*' in bar_config['screens']:
                for screen in self._app.screens():
                    bar_options = self._build_bar_options(bar_config, bar_index, bar_name)
                    bar = Bar(**bar_options, bar_screen=screen)
                    self._bars.append(bar)
            else:
                for screen_name in bar_config['screens']:
                    screen = self._get_screen_by_name(screen_name)
                    if screen:
                        bar_options = self._build_bar_options(bar_config, bar_index, bar_name)
                        bar = Bar(**bar_options, bar_screen=screen)
                        self._bars.append(bar)

        self._widget_builder.raise_alerts_if_errors_present()

    def _build_bar_options(self, bar_config, bar_index, bar_name):
        bar_options = deepcopy(bar_config)
        bar_widgets, widget_event_listeners = self._widget_builder.build_widgets(bar_options.get('widgets', {}))

        bar_options['bar_index'] = bar_index
        bar_options['bar_name'] = bar_name
        bar_options['stylesheet'] = self._stylesheet.cssText.decode('utf-8')
        bar_options['widgets'] = bar_widgets

        self.widget_event_listeners = self.widget_event_listeners.union(widget_event_listeners)

        del bar_options['enabled']
        del bar_options['screens']

        return bar_options

    def _get_screen_by_name(self, screen_name: str):
        return next(filter(lambda scr: screen_name in scr.name(), self._app.screens()), None)

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
