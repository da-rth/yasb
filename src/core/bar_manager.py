import logging
import uuid
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from cssutils.css import CSSStyleSheet
from core.bar import Bar
from core.utils.widget_builder import WidgetBuilder
from core.event_service import EventService
from copy import deepcopy


class BarManager(QObject):

    screen_disconnect = pyqtSignal(QScreen)

    def __init__(self, config: dict, stylesheet: CSSStyleSheet):
        super().__init__()
        self.config = config
        self.stylesheet = stylesheet
        self.event_service = EventService()
        self.widget_event_listeners = set()
        self.bars: list[Bar] = list()
        self.config['bars'] = {n: bar for n, bar in self.config['bars'].items() if bar['enabled']}

        self._threads = {}
        self._active_listeners = {}
        self._widget_builder = WidgetBuilder(self.config['widgets'])
        self.screen_disconnect.connect(self.on_screen_connect)

    def on_screen_disconnect(self, screen: QScreen) -> None:
        logging.info(f"Screen disconnected: {screen.name()}")
        for bar_idx in self._get_bar_idxs_by_screen_name(screen.name()):
            self.bars[bar_idx].close()
            self.bars[bar_idx] = None

    def on_screen_connect(self, screen: QScreen) -> None:
        logging.info(f"Screen connected: {screen.name()}")
        for bar_name, bar_config in self.config['bars'].items():
            if '*' in bar_config['screens'] or screen.name() in bar_config['screens']:
                self.create_bar(bar_config, bar_name, screen)

    def _get_bar_idxs_by_screen_name(self, screen_name: str) -> list[int]:
        return [i for i, bar in enumerate(self.bars) if bar.screen_name == screen_name]

    def _get_screen_by_name(self, screen_name: str) -> QScreen:
        return next(filter(lambda scr: screen_name in scr.name(), QApplication.screens()), None)

    def run_listeners_in_threads(self):
        for listener in self.widget_event_listeners:
            logging.info(f"Starting '{listener.__name__}'")
            thread = QThread()
            event_listener = listener()
            event_listener.moveToThread(thread)
            thread.started.connect(event_listener.start)
            thread.start()
            self._active_listeners[listener] = event_listener
            self._threads[listener] = thread

    def stop_listener_threads(self):
        for listener in self.widget_event_listeners:
            self._active_listeners[listener].stop()
            self._threads[listener].terminate()
            del self._threads[listener]
            del self._active_listeners[listener]

    def close_all_bars(self):
        self.stop_listener_threads()

        for bar in self.bars:
            logging.info(f"Closing bar '{self.bar_id}'")
            bar.close()

        self.event_service.clear()
        self.bars.clear()

    def initialize_bars(self) -> None:
        self._widget_builder = WidgetBuilder(self.config['widgets'])

        for bar_name, bar_config in self.config['bars'].items():

            if '*' in bar_config['screens']:
                for screen in QApplication.screens():
                    self.create_bar(bar_config, bar_name, screen)
                return

            for screen_name in bar_config['screens']:
                screen = self._get_screen_by_name(screen_name)
                if screen:
                    self.create_bar(bar_config, bar_name, screen)

        self._widget_builder.raise_alerts_if_errors_present()

    def create_bar(self, config: dict, name: str, screen: QScreen) -> None:
        screen_name = screen.name().replace('\\', '').replace('.', '')
        bar_id = f"{name}_{screen_name}_{str(uuid.uuid4())[:8]}"
        logging.info(f"Creating bar '{bar_id}' {screen.geometry().getRect()}")

        bar_config = deepcopy(config)
        bar_widgets, widget_event_listeners = self._widget_builder.build_widgets(bar_config.get('widgets', {}))
        bar_options = {
            **bar_config,
            'bar_id': bar_id,
            'bar_name': name,
            'bar_screen': screen,
            'stylesheet': self.stylesheet.cssText.decode('utf-8'),
            'widgets': bar_widgets
        }

        del bar_options['enabled']
        del bar_options['screens']

        self.widget_event_listeners = self.widget_event_listeners.union(widget_event_listeners)
        self.bars.append(Bar(**bar_options))
