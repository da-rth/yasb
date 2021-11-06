import sys
from PyQt6.QtWidgets import QApplication
from core.bar_manager import BarManager
from core.utils.config_loader import get_config_and_stylesheet
from core.utils.alert_dialog import raise_info_alert
from core.utils.komorebi.event_listener import KomorebiEventListener
from core.utils.win32.event_listener import Win32EventListener

DEBUG_MODE = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config, stylesheet = get_config_and_stylesheet(DEBUG_MODE)
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

    komorebi_event_listener = KomorebiEventListener()
    win32_event_listener = Win32EventListener()

    manager.add_background_task(komorebi_event_listener.listen_for_events)
    manager.add_background_task(win32_event_listener.listen_for_events)

    manager.show_bars()
    manager.run_background_tasks()

    sys.exit(app.exec())
