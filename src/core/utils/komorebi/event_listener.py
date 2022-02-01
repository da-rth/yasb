import logging
import time

import win32pipe
import win32file
import json
from PyQt6.QtCore import pyqtSignal, QObject
from core.event_enums import KomorebiEvent
from core.event_service import EventService
from core.event_enums import BarEvent
from core.utils.komorebi.client import KomorebiClient

KOMOREBI_PIPE_BUFF_SIZE = 64 * 1024
KOMOREBI_PIPE_NAME = "yasb"


class KomorebiEventListener(QObject):
    app_exit_signal = pyqtSignal()

    def __init__(
            self,
            pipe_name: str = KOMOREBI_PIPE_NAME,
            buffer_size: int = KOMOREBI_PIPE_BUFF_SIZE,
            background_interval: int = 2000
    ):
        super().__init__()
        self._komorebic = KomorebiClient()
        self.pipe_name = pipe_name
        self.buffer_size = buffer_size
        self.event_service = EventService()
        self.pipe = None
        self._app_running = True
        self.event_service.register_event(BarEvent.ExitApp, self.app_exit_signal)
        self.app_exit_signal.connect(self._on_exit)
        self._pause_background_updater = False

    def __str__(self):
        return "Komorebi Event Listener"

    def _on_exit(self):
        self._app_running = False

    def _create_pipe(self) -> None:
        pipe_name_full = f"\\\\.\\pipe\\{self.pipe_name}"
        open_mode = win32pipe.PIPE_ACCESS_DUPLEX
        pipe_mode = win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT
        max_instances = 1
        buffer_size_in = self.buffer_size
        buffer_size_out = self.buffer_size
        default_timeout_ms = 0
        security_attributes = None

        self.pipe = win32pipe.CreateNamedPipe(
            pipe_name_full,
            open_mode,
            pipe_mode,
            max_instances,
            buffer_size_in,
            buffer_size_out,
            default_timeout_ms,
            security_attributes
        )

    def start(self):
        self._pause_background_updater = True
        self._create_pipe()
        self._wait_until_komorebi_online()

        try:
            while self._app_running:
                result, data = win32file.ReadFile(self.pipe, self.buffer_size, None)

                if not data.strip():
                    continue

                try:
                    event_message = json.loads(data.decode("utf-8"))
                    event = event_message['event']
                    state = event_message['state']

                    if event and state:
                        self._emit_event(event, state)
                except (KeyError, ValueError):
                    logging.exception(f"Failed parse komorebi state. Received data: {data}")
        except Exception:
            logging.exception(f"Komorebi has disconnected from the named pipe {self.pipe_name}")
            win32file.CloseHandle(self.pipe)
            self.event_service.emit_event(KomorebiEvent.KomorebiDisconnect)
            self.start()

    def _emit_event(self, event: dict, state: dict) -> None:
        try:
            event_name = event['type']
            self.event_service.emit_event(KomorebiEvent.KomorebiUpdate, event, state)
            if event_name in KomorebiEvent:
                self.event_service.emit_event(KomorebiEvent[event_name], event, state)
        except (KeyError, TypeError):
            logging.exception(f"Failed to emit komorebi event {event_name}: {event_name} ")

    def _wait_until_komorebi_online(self):
        logging.info(f"Waiting for Komorebi to subscribe to named pipe {self.pipe_name}")
        self._komorebic.wait_until_subscribed_to_pipe(self.pipe_name)
        self._pause_background_updater = False
        win32pipe.ConnectNamedPipe(self.pipe, None)
        logging.info(f"Komorebi connected to named pipe: {self.pipe_name}")
        state = self._komorebic.query_state()

        while state is None and self._app_running:
            logging.error(
                "Failed to retrieve komorebi state before starting event listener: None returned. "
                "Retrying in 1 second... Is komorebi online and its binaries added to $PATH?"
            )
            time.sleep(1)
            state = self._komorebic.query_state()

        self.event_service.emit_event(KomorebiEvent.KomorebiConnect, state)
