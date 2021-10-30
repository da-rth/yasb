import ctypes
import time
from PyQt6.QtCore import QObject
from win32gui import GetForegroundWindow
from core.utils.win32.windows import WinEventProcType, WinEvent, user32, ole32, msg
from core.event_service import EventService
from core.utils.win32.utilities import get_hwnd_info


class Win32EventListener(QObject):
    def __init__(self):
        super().__init__()
        self._event_service = EventService()
        self._win_event_process = WinEventProcType(self._event_handler)

    def _event_handler(self, win_event_hook, event, hwnd, id_object, id_child, event_thread, event_time) -> None:
        if event in WinEvent:
            hwnd_info = get_hwnd_info(hwnd)
            event_type = WinEvent._value2member_map_[event]
            self._event_service.emit_event(event_type, hwnd_info)

    def _build_event_hook(self) -> int:
        # Hooks onto System events only
        return user32.SetWinEventHook(
            WinEvent.EventMin.value,
            WinEvent.EventSystemEnd.value,
            0,
            self._win_event_process,
            0,
            0,
            WinEvent.WinEventOutOfContext.value
        )

    def _emit_foreground_window_event(self):
        foreground_window_hwnd = GetForegroundWindow()
        foreground_window_info = get_hwnd_info(foreground_window_hwnd)
        self._event_service.emit_event(WinEvent.EventSystemForeground, foreground_window_info)

    def listen_for_events(self):
        hook = self._build_event_hook()

        if hook == 0:
            print("SetWinEventHook failed. Retrying indefinitely...")
        while hook == 0:
            time.sleep(1)
            hook = self._build_event_hook()

        print("SetWinEventHook Successful. Emitting focused window and waiting for events.")
        self._emit_foreground_window_event()

        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)

        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()
