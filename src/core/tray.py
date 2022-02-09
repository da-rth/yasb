import logging
import webbrowser
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication, QSize
from core.bar_manager import BarManager
from settings import GITHUB_URL, FAVICON_PATH, APP_NAME, APP_NAME_FULL


class TrayIcon(QSystemTrayIcon):

    def __init__(self, bar_manager: BarManager):
        QSystemTrayIcon.__init__(self)
        self._bar_manager = bar_manager
        self._docs_url = GITHUB_URL
        self._icon = QIcon()
        self._load_favicon()
        self._load_context_menu()
        self.setToolTip(f"{APP_NAME} - {APP_NAME_FULL}")

    def _load_favicon(self):
        self._icon.addFile(f'{FAVICON_PATH}/favicon-16x16.png', QSize(16, 16))
        self._icon.addFile(f'{FAVICON_PATH}/favicon-32x32.png', QSize(32, 32))
        self._icon.addFile(f'{FAVICON_PATH}/favicon-152x152.png', QSize(152, 152))
        self._icon.addFile(f'{FAVICON_PATH}/favicon-192x192.png', QSize(192, 192))
        self._icon.addFile(f'{FAVICON_PATH}/favicon-512x512.png', QSize(512, 512))
        self.setIcon(self._icon)

    def _load_context_menu(self):
        menu = QMenu()
        github_action = menu.addAction("Visit GitHub")
        github_action.triggered.connect(self._open_docs_in_browser)

        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self._exit_application)

        self.setContextMenu(menu)

    def _exit_application(self):
        self._bar_manager.close_bars()
        logging.info("Tray Exit Button selected. Exiting Application...")
        QCoreApplication.exit(0)

    def _open_docs_in_browser(self):
        webbrowser.open(self._docs_url)
