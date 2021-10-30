from win32api import MonitorFromWindow


def get_monitor_hwnd(window_hwnd: int) -> int:
    return int(MonitorFromWindow(window_hwnd))
