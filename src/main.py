import sys
from PyQt6.QtWidgets import QApplication
from core.bar_manager import BarManager
from core.utils.config_loader import get_config_and_stylesheet
from core.utils.alert_dialog import raise_info_alert
from core.tray import TrayIcon
from core import settings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

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
    sys.exit(app.exec())
