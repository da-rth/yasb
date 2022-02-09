from sys import argv, exit
from PyQt6.QtWidgets import QApplication
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
    manager.initialize_bars(app_init=True)
    manager.run_listeners_in_threads()

    # Build system tray icon
    tray_icon = TrayIcon(manager)
    tray_icon.show()

    # Initialise file watcher
    observer = create_observer(manager)
    observer.start()

    # Start Application
    exit_status = app.exec()
    observer.stop()
    observer.join()
    exit(exit_status)


if __name__ == "__main__":
    init_logger()
    main()
