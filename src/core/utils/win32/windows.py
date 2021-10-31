import ctypes.wintypes
from core.event_enums import Event

user32 = ctypes.windll.user32
user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

ole32 = ctypes.windll.ole32
ole32.CoInitialize(0)

msg = ctypes.wintypes.MSG()

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)


class WinEvent(Event):
    """
    Win32 Event Constants

    More information: https://docs.microsoft.com/en-us/windows/win32/winauto/event-constants
    """
    EventMin = 0x00000001
    EventMax = 0x7FFFFFFF
    EventSystemEnd = 0x00FF

    WinEventOutOfContext = 0x0000
    EventSystemSound = 0x0001
    EventSystemAlert = 0x0002
    EventSystemForeground = 0x0003
    EventSystemMenuStart = 0x0004
    EventSystemMenuEnd = 0x0005
    EventSystemMenuPopupStart = 0x0006
    EventSystemMenuPopupEnd = 0x0007
    EventSystemCaptureStart = 0x0008
    EventSystemCaptureEnd = 0x0009
    EventSystemDialogStart = 0x0010
    EventSystemDialogEnd = 0x0011
    EventSystemScrollingStart = 0x0012
    EventSystemScrollingEnd = 0x0013
    EventSystemSwitchStart = 0x0014
    EventSystemSwitchEnd = 0x0015
    EventSystemMinimizeStart = 0x0016
    EventSystemMinimizeEnd = 0x0017
    EventSystemMoveSizeStart = 0x000A
    EventSystemMoveSizeEnd = 0x000B
