import sys
import traceback
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

PROGRAM_NAME = "Yasb"


class AlertDialog(QMessageBox):

    def __init__(
            self,
            title: str,
            message: str,
            informative_message: str = None,
            icon: QMessageBox.Icon = QMessageBox.Icon.Information,
            show_quit: bool = False,
            show_ok: bool = False,
            additional_details: str = None
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.setIcon(icon)
        self.setText(message)

        if informative_message:
            self.setInformativeText(informative_message)

        if additional_details:
            self.setDetailedText(additional_details)

        self.ok_button = self.addButton('Ok', QMessageBox.ButtonRole.AcceptRole) if show_ok else None
        self.quit_button = self.addButton('Quit', QMessageBox.ButtonRole.DestructiveRole) if show_quit else None

    def show(self) -> None:
        self.exec()

        if self.clickedButton() == self.quit_button:
            sys.exit()


def raise_error_alert(title, msg, informative_msg, rich_text=False):
    alert = AlertDialog(
        icon=QMessageBox.Icon.Critical,
        title=f"{PROGRAM_NAME}: {title}",
        message=msg,
        informative_message=informative_msg,
        additional_details=traceback.format_exc(),
        show_quit=True
    )

    if rich_text:
        alert.setTextFormat(Qt.TextFormat.RichText)

    alert.show()
    sys.exit()


def raise_info_alert(title, msg, informative_msg, rich_text=False, exit_on_close=False):
    alert = AlertDialog(
        icon=QMessageBox.Icon.Information,
        title=f"{PROGRAM_NAME}: {title}",
        message=msg,
        informative_message=informative_msg
    )

    if rich_text:
        alert.setTextFormat(Qt.TextFormat.RichText)

    alert.show()

    if exit_on_close:
        sys.exit()
