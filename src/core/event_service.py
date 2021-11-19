import functools
import logging

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any
from core.event_enums import Event


@functools.lru_cache()
class EventService(QObject):
    def __init__(self):
        super().__init__()
        self._registered_event_signals: dict[Event, list[pyqtSignal]] = {}

    def register_event(self, event_type: Event, event_signal: pyqtSignal):
        if event_type not in self._registered_event_signals:
            self._registered_event_signals[event_type] = [event_signal]
        else:
            self._registered_event_signals[event_type].append(event_signal)

    def emit_event(self, event_type: Event, *args: Any):
        event_signals = self._registered_event_signals.get(event_type, [])
        for event_signal in event_signals:
            try:
                event_signal.emit(*args)
            except Exception:
                logging.exception(f"Failed to emit event signal {event_signal} with args: {args}")
