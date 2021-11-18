import ctypes
import time
from PyQt6.QtCore import QObject, pyqtSignal
from win32gui import GetForegroundWindow
from core.utils.win32.windows import WinEventProcType, WinEvent, user32, ole32, msg
from core.event_service import EventService
from core.utils.win32.utilities import get_hwnd_info
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

    def _event_handler(self, win_event_hook, event, hwnd, id_object, id_child, event_thread, event_time) -> None:
        if not self._app_running:
            self._quit()

        elif event in WinEvent:
            event_type = WinEvent._value2member_map_[event]
            event_info = get_hwnd_info(hwnd, event_type)
            self._event_service.emit_event(event_type, event_info)

    def _build_event_hook(self) -> int:
        # Hooks onto System events only
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
        foreground_window_info = get_hwnd_info(foreground_window_hwnd, foreground_event)
        self._event_service.emit_event(foreground_event, foreground_window_info)

    def start(self):
        print("[Run Once] Initialising win32 event listener")
        self._hook = self._build_event_hook()

        if self._hook == 0:
            print("SetWinEventHook failed. Retrying indefinitely...")
        while self._hook == 0:
            time.sleep(1)
            self._hook = self._build_event_hook()

        print("SetWinEventHook Successful. Emitting focused window and waiting for events.")
        self._emit_foreground_window_event()

        if user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) == 0:
            self._quit()

    def _quit(self):
        print("Exiting Win32 event listener")
        user32.UnhookWinEvent(self._hook)
        ole32.CoUninitialize()
        self.exit()
