import os
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from core.bar_manager import BarManager
from core.utils.config_utils import get_config_and_stylesheet, get_config_dir
from core.utils.alert_dialog import raise_info_alert
from core.tray import TrayIcon
from core.settings import DEFAULT_LOG_FILENAME, APP_NAME
from core import settings
# from core.utils.win32.active_window_border import ActiveWindowBorder

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
    print("Logging to", LOG_PATH)

    logging.info(f"Starting {APP_NAME}")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    font = QFont("Courier New")
    font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(font)

    config, stylesheet = get_config_and_stylesheet(settings.DEBUG_MODE)

    manager = BarManager(app, config, stylesheet)
    manager.initialize_bars()

    if manager.num_bars() == 0:
        raise_info_alert(
            title="No bars added",
            msg="Your config must specify the name of the screen where your bar will appear",
            informative_msg=(
                "Tip: try setting <pre>\"screen\": \"all\"</pre>"
                "to display your bar on all screens."
            ),
            rich_text=True,
            exit_on_close=True
        )

    manager.run_listeners_in_threads()

    trayIcon = TrayIcon(manager)
    trayIcon.show()

    manager.show_bars()

    # Experimental Feature
    # awb = ActiveWindowBorder()

    sys.exit(app.exec())
