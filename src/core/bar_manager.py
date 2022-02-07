import logging
import uuid
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QThread, QObject, Qt, pyqtSignal, pyqtSlot
from core.bar import Bar
from core.utils.widget_builder import WidgetBuilder
from core.event_service import EventService
from core.config import get_stylesheet, get_config
from copy import deepcopy
from contextlib import suppress
from ratelimit import limits


class BarManager(QObject):
    styles_modified = pyqtSignal()
    config_modified = pyqtSignal()
    screen_disconnect = pyqtSignal(QScreen)

    def __init__(self, config: dict, stylesheet: str):
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

        self.styles_modified.connect(self.on_styles_modified, type=Qt.ConnectionType.UniqueConnection)
        self.config_modified.connect(self.on_config_modified, type=Qt.ConnectionType.UniqueConnection)

    @pyqtSlot()
    @limits(calls=1, period=1, raise_on_limit=False)
    def on_styles_modified(self):
        logging.info(f"Stylesheet file has been modified. Attempting to retrieve new stylesheet.")
        stylesheet = get_stylesheet(show_error_dialog=True)

        if stylesheet:
            self.stylesheet = stylesheet
            for bar in self.bars:
                bar.setStyleSheet(self.stylesheet)
            logging.info("Successfully loaded updated stylesheet and applied to all bars.")

    @pyqtSlot()
    @limits(calls=1, period=1, raise_on_limit=False)
    def on_config_modified(self):
        logging.info(f"Config file has been modified. Attempting to reload all bars.")
        config = get_config(show_error_dialog=True)

        if config:
            self.config = config
            self.close_all_bars()
            self.initialize_bars()
            logging.info("Successfully loaded updated config and re-initialised all bars.")

    @pyqtSlot(QScreen)
    def on_screen_disconnect(self, screen: QScreen) -> None:
        logging.info(f"Screen disconnected: {screen.name()}")
        for bar_idx in self._get_bar_idxs_by_screen_name(screen.name()):
            with suppress(IndexError):
                bar = self.bars.pop(bar_idx)
                bar.close()

    @pyqtSlot(QScreen)
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
            thread = listener()
            thread.start()
            self._threads[listener] = thread

    def stop_listener_threads(self):
        try:
            for listener in self.widget_event_listeners:
                self._threads[listener].stop()
                self._threads[listener].quit()
                self._threads[listener].wait(500)
            self._threads.clear()
        except Exception as e:
            print(e)

    def close_all_bars(self):
        self.stop_listener_threads()

        for bar in self.bars:
            logging.info(f"Closing bar '{bar.bar_id}'")
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
        logging.info(f"Creating bar '{bar_id}' on screen {screen.geometry().getRect()}")

        bar_config = deepcopy(config)
        bar_widgets, widget_event_listeners = self._widget_builder.build_widgets(bar_config.get('widgets', {}))
        bar_options = {
            **bar_config,
            'bar_id': bar_id,
            'bar_name': name,
            'bar_screen': screen,
            'stylesheet': self.stylesheet,
            'widgets': bar_widgets
        }

        del bar_options['enabled']
        del bar_options['screens']

        self.widget_event_listeners = self.widget_event_listeners.union(widget_event_listeners)
        self.bars.append(Bar(**bar_options))
