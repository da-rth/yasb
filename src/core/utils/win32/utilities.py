import traceback

import psutil
from win32process import GetWindowThreadProcessId
from win32gui import GetWindowText, GetClassName, GetWindowRect
from win32api import MonitorFromWindow, GetMonitorInfo


def get_monitor_hwnd(window_hwnd: int) -> int:
    return int(MonitorFromWindow(window_hwnd))


def get_monitor_info(monitor_hwnd: int):
    monitor_info = GetMonitorInfo(monitor_hwnd)
    return {
        'rect': {
            'x': monitor_info['Monitor'][0],
            'y': monitor_info['Monitor'][1],
            'width': monitor_info['Monitor'][2],
            'height': monitor_info['Monitor'][3]
        },
        'rect_work_area': {
            'x': monitor_info['Work'][0],
            'y': monitor_info['Work'][1],
            'width': monitor_info['Work'][2],
            'height': monitor_info['Work'][3]
        },
        'flags': monitor_info['Flags'],
        'device': monitor_info['Device']
    }


def get_hwnd_info(hwnd: int) -> dict:
    process_id = GetWindowThreadProcessId(hwnd)
    process = psutil.Process(process_id[-1])
    window_rect = GetWindowRect(hwnd)
    window_rect = {
        'x': window_rect[0],
        'y': window_rect[1],
        'width': window_rect[2],
        'height': window_rect[3]
    }

    try:
        monitor_hwnd = get_monitor_hwnd(hwnd)
        monitor_info = get_monitor_info(monitor_hwnd)
    except Exception:
        monitor_hwnd = None
        monitor_info = {}
        print(traceback.format_exc())

    return {
        'title': GetWindowText(hwnd),
        'class_name': GetClassName(hwnd),
        'process': process.name(),
        'pid': process.pid,
        'hwnd': hwnd,
        'monitor_hwnd': monitor_hwnd,
        'monitor_info': monitor_info,
        'rect': window_rect
    }
