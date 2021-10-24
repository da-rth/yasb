import sys
from PyQt6.QtWidgets import QApplication
from core.bar_manager import BarManager
from core.config_parser import get_config, get_stylesheet
from core.alert_dialog import raise_error_alert, raise_info_alert

DEBUG = True
ISSUES_URL = "https://github.com/denBot/yasb/issues"

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

if __name__ == "__main__":
    try:
        screens = app.screens()
        manager = BarManager()
        config = get_config()
        stylesheet = get_stylesheet()

        for bar_config in config['bars']:
            if bar_config['screen'] == "all":
                for screen in screens:
                    print("Adding bar to", screen.name())
                    manager.add_bar(screen, bar_config, stylesheet)
            else:
                screen_name = bar_config['screen']
                matched_screen = next(filter(lambda screen: screen_name in screen.name(), screens), None)
                if matched_screen:
                    print("Adding bar to", matched_screen.name())
                    manager.add_bar(matched_screen, bar_config, stylesheet)

        if len(manager.bars) == 0:
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

        manager.show_bars()
        sys.exit(app.exec())

    except Exception:
        if DEBUG:
            raise Exception

        raise_error_alert(
            title="Program Error",
            msg="This application has encountered a critical error. Sorry about that.",
            informative_msg=(
                f"You can <strong>submit a bug report</strong> at:"
                f"<br/><br/><a href='{ISSUES_URL}'>{ISSUES_URL}</a><br/><br/>"
                "Please click 'Show Details' for more information."
            ),
            rich_text=True
        )
