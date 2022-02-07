import logging
from os.path import basename
from PyQt6.QtCore import QObject, pyqtSignal
from core.config import get_config_dir
from settings import DEFAULT_STYLES_FILENAME, DEFAULT_CONFIG_FILENAME
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileModifiedEvent


class FileModifiedEventHandler(PatternMatchingEventHandler):
    styles_file = DEFAULT_STYLES_FILENAME
    config_file = DEFAULT_CONFIG_FILENAME

    def __init__(self, styles_signal: pyqtSignal, config_signal: pyqtSignal):
        super().__init__()
        self.styles_signal = styles_signal
        self.config_signal = config_signal
        self._patterns = [
            self.styles_file,
            self.config_file
        ]
        self._ignore_patterns = []
        self._ignore_directories = True
        self._case_sensitive = False

    def on_modified(self, event: FileModifiedEvent):
        modified_file = basename(event.src_path)

        if modified_file == self.styles_file:
            self.styles_signal.emit()
        elif modified_file == self.config_file:
            self.config_signal.emit()


def create_observer(styles_signal: pyqtSignal, config_signal: pyqtSignal):
    event_handler = FileModifiedEventHandler(styles_signal, config_signal)
    config_path = get_config_dir()
    observer = Observer()
    observer.schedule(event_handler, path=config_path, recursive=False)
    logging.info(f"Created file watcher for path {config_path}")
    return observer
