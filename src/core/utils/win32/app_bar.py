import ctypes
import win32api
import logging
from ctypes import wintypes, Structure, POINTER, sizeof, windll, c_ulong
from PyQt6.QtWidgets import QWidget


shell32 = windll.shell32
user32 = windll.user32

"""
Application Desktop Toolbar (with added support for PyQt6)

https://docs.microsoft.com/en-us/windows/win32/shell/application-desktop-toolbars
"""


class AppBarData(Structure):
    """
    AppBarData struct
    Documentation: https://docs.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-appbardata#syntax
    """
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", ctypes.c_ulong),
        ("uEdge", c_ulong),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]


class AppBarEdge:
    """
    A value that specifies the edge of the screen.
    Documentation: https://docs.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-appbardata#members
    """
    Left = 0
    Top = 1
    Right = 2
    Bottom = 3


class AppBarMessage:
    """
    SHAppBarMessage App Bar Messages
    Documentation: https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shappbarmessage
    """
    New = 0
    Remove = 1
    QueryPos = 2
    SetPos = 3
    GetState = 4
    GetTaskbarPos = 5
    Activate = 6
    GetAutoHideBar = 7
    SetAutoHideBar = 8
    WindowPosChanged = 9
    SetState = 10
    GetAutoHideBarEx = 11
    SetAutoHideBarEx = 12


AppBarDataPointer = POINTER(AppBarData)


class Win32AppBar:

    def __init__(self, window: QWidget, edge: AppBarEdge):
        self.window = window
        self.app_bar_data = AppBarData()
        self.app_bar_data.cbSize = wintypes.DWORD(sizeof(self.app_bar_data))
        self.app_bar_data.uEdge = edge

    def create_appbar(self):
        logging.info(f"Creating Win32 App Bar for bar {self.window.bar_index} with HWND {int(self.window.winId())}")
        self.app_bar_data.hWnd = self.window.winId().__int__()
        screen_geometry = self.window.screen().geometry()
        win32api.RegisterWindowMessage("AppBarMessage")
        shell32.SHAppBarMessage(AppBarMessage.New, AppBarDataPointer(self.app_bar_data))
        pixel_ratio = self.window.screen().devicePixelRatio()
        self.app_bar_data.rc.left = screen_geometry.x()
        self.app_bar_data.rc.right = screen_geometry.height()

        """
        # Vertical Bar Alignment
        if self.app_bar_data.uEdge in [AppBarEdge.Left, AppBarEdge.Right]:
            self.app_bar_data.rc.top = screen_geometry.y()
            self.app_bar_data.rc.bottom = int(screen_geometry.height() * pixel_ratio)

            if self.app_bar_data.uEdge == AppBarEdge.Left:
                self.app_bar_data.rc.left = screen_geometry.x()
                self.app_bar_data.rc.right = self.window.width()
            else:
                self.app_bar_data.rc.right = screen_geometry.width()
                self.app_bar_data.rc.left = screen_geometry.width() - self.window.width()
        """
        if self.app_bar_data.uEdge == AppBarEdge.Top:
            self.app_bar_data.rc.top = int(screen_geometry.y() * pixel_ratio)
            self.app_bar_data.rc.bottom = int(self.window.height() * pixel_ratio)
        else:
            self.app_bar_data.rc.bottom = int(screen_geometry.height() * pixel_ratio)
            self.app_bar_data.rc.top = int((screen_geometry.height() - self.window.height()) * pixel_ratio)

        shell32.SHAppBarMessage(AppBarMessage.QueryPos, AppBarDataPointer(self.app_bar_data))
        shell32.SHAppBarMessage(AppBarMessage.SetPos, AppBarDataPointer(self.app_bar_data))

    def remove_appbar(self):
        logging.info(f"Removing Win32 App Bar for HWND {self.app_bar_data.hWnd}")
        shell32.SHAppBarMessage(AppBarMessage.Remove, AppBarDataPointer(self.app_bar_data))
