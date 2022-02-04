import os
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from settings import DEFAULT_LOG_FILENAME, APP_NAME, APP_NAME_FULL
from core.bar_manager import BarManager
from core.utils.config_utils import get_config_and_stylesheet, get_config_dir
from core.tray import TrayIcon


LOG_PATH = os.path.join(get_config_dir(), DEFAULT_LOG_FILENAME)

logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(get_config_dir(), DEFAULT_LOG_FILENAME),
    format="%(asctime)s %(levelname)s %(filename)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w",
)

logging.getLogger().addHandler(logging.StreamHandler())


if __name__ == "__main__":
    logging.info(f"Starting {APP_NAME} - {APP_NAME_FULL}")
    config, stylesheet = get_config_and_stylesheet()

    if not config or not stylesheet:
        sys.exit()

    app = QApplication(sys.argv)
    manager = BarManager(config, stylesheet)
    manager.initialize_bars()
    manager.run_listeners_in_threads()

    if not manager.bars:
        logging.warning(
            "No bars added. You must specify the screen name(s) on which your bar(s) will appear within the config."
        )

    app.setQuitOnLastWindowClosed(False)
    app.screenAdded.connect(manager.on_screen_connect, type=Qt.ConnectionType.QueuedConnection)
    app.screenRemoved.connect(manager.on_screen_disconnect)

    trayIcon = TrayIcon(manager)
    trayIcon.show()

    sys.exit(app.exec())
