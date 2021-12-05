import ctypes
import time
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from win32gui import GetForegroundWindow
from core.utils.win32.windows import WinEventProcType, WinEvent, user32, ole32, msg
from core.event_service import EventService
from core.event_enums import BarEvent


class SystemEventListener(QObject):
    app_exit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._hook = None
        self._app_running = True
        self._event_service = EventService()
        self._win_event_process = WinEventProcType(self._event_handler)
        self._event_service.register_event(BarEvent.ExitApp, self.app_exit_signal)
        self.app_exit_signal.connect(self._on_exit)

    def __str__(self):
        return "Win32 System Event Listener"

    def _event_handler(
        self,
        _win_event_hook,
        event,
        hwnd,
        _id_object,
        _id_child,
        _event_thread,
        _event_time
    ) -> None:
        if not self._app_running:
            self._quit()
        elif event in WinEvent:
            try:
                if event in WinEvent:
                    event_type = WinEvent._value2member_map_[event]
                    self._event_service.emit_event(event_type, hwnd, event_type)
            except Exception:
                logging.exception(f"Failed to emit event {event_type} for {hwnd}")

    def _build_event_hook(self) -> int:
        return user32.SetWinEventHook(
            WinEvent.EventMin.value,
            WinEvent.EventObjectEnd.value,
            0,
            self._win_event_process,
            0,
            0,
            WinEvent.WinEventOutOfContext.value
        )

    def _on_exit(self):
        self._app_running = False

    def _emit_foreground_window_event(self):
        foreground_event = WinEvent.EventSystemForeground
        foreground_window_hwnd = GetForegroundWindow()

        if foreground_window_hwnd:
            self._event_service.emit_event(foreground_event, foreground_window_hwnd, foreground_event)

    def start(self):
        self._hook = self._build_event_hook()

        if self._hook == 0:
            logging.warning("SetWinEventHook failed. Retrying indefinitely...")

        while self._hook == 0:
            time.sleep(1)
            self._hook = self._build_event_hook()

        logging.info("SetWinEventHook Successful. Emitting focused window and waiting for events.")
        self._emit_foreground_window_event()

        user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)

    def _quit(self):
        logging.info("Exiting Win32 event listener")
        user32.UnhookWinEvent(self._hook)
        ole32.CoUninitialize()
