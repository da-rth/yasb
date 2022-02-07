from sys import argv, exit
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.bar_manager import BarManager
from core.config import get_config_and_stylesheet
from core.log import init_logger
from core.tray import TrayIcon
from core.watcher import create_observer


def main():
    config, stylesheet = get_config_and_stylesheet()

    app = QApplication(argv)
    app.setQuitOnLastWindowClosed(False)

    # Initialise bars and background event listeners
    manager = BarManager(config, stylesheet)
    manager.initialize_bars()
    manager.run_listeners_in_threads()

    # Add screen connect/disconnect event listeners
    app.screenAdded.connect(manager.on_screen_connect, type=Qt.ConnectionType.QueuedConnection)
    app.screenRemoved.connect(manager.on_screen_disconnect)

    # Build system tray icon
    tray_icon = TrayIcon(manager)
    tray_icon.show()

    # Initialise file watcher
    observer = create_observer(
        manager.styles_modified,
        manager.config_modified
    )
    observer.start()

    # Start Application
    exit_status = app.exec()
    observer.stop()
    observer.join()
    exit(exit_status)


if __name__ == "__main__":
    init_logger()
    main()
