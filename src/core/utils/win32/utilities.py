import traceback
import psutil
import pywintypes
from core.utils.win32.windows import WinEvent
from win32process import GetWindowThreadProcessId
from win32gui import GetWindowText, GetClassName, GetWindowRect
from win32api import MonitorFromWindow, GetMonitorInfo


def get_monitor_hwnd(window_hwnd: int) -> int:
    return int(MonitorFromWindow(window_hwnd))


def get_monitor_info(monitor_hwnd: int) -> dict:
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


def get_process_info(hwnd: int) -> dict:
    try:
        process_id = GetWindowThreadProcessId(hwnd)
        process = psutil.Process(process_id[-1])
        return {
            'name': process.name(),
            'pid': process.pid,
            'ppid': process.ppid,
            'cpu_percent': process.cpu_percent,
            'mem_percent': process.memory_percent,
            'num_threads': process.num_threads,
            'username': process.username,
            'status': process.status
        }
    except (ValueError, IndexError, psutil.NoSuchProcess):
        return {
            'name': 'name unknown',
            'pid': 'pid unknown',
            'ppid': 'ppid unknown',
            'cpu_num': 'cpu_num unknown',
            'cpu_percent': 'cpu_percent unknown',
            'mem_percent': 'mem_percent unknown',
            'num_threads': 'num_threads unknown',
            'username': 'username unknown',
            'status': 'status unknown'
        }


def get_window_rect(hwnd: int) -> dict:
    try:
        window_rect = GetWindowRect(hwnd)
        return {
            'x': window_rect[0],
            'y': window_rect[1],
            'width': window_rect[2],
            'height': window_rect[3]
        }
    except (pywintypes.error, IndexError):
        return {
            'x': 0,
            'y': 0,
            'width': 0,
            'height': 0
        }


def get_class_name(hwnd: int) -> str:
    try:
        return GetClassName(hwnd)
    except pywintypes.error:
        return 'unknown class'


def get_window_text(hwnd: int) -> str:
    try:
        return GetWindowText(hwnd)
    except pywintypes.error:
        return ''


def get_hwnd_info(hwnd: int, event: WinEvent) -> dict:
    try:
        try:
            monitor_hwnd = get_monitor_hwnd(hwnd)
            monitor_info = get_monitor_info(monitor_hwnd)
        except Exception:
            monitor_hwnd = None
            monitor_info = {}

        return {
            'hwnd': hwnd,
            'event': event,
            'title': get_window_text(hwnd),
            'class_name': get_class_name(hwnd),
            'process': get_process_info(hwnd),
            'monitor_hwnd': monitor_hwnd,
            'monitor_info': monitor_info,
            'rect': get_window_rect(monitor_hwnd)
        }
    except Exception:
        print(traceback.format_exc())
