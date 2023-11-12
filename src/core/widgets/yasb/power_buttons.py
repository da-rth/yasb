import subprocess
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.power_buttons import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6 import QtCore, QtGui


class PowerWidgetButton(QPushButton):
    def __init__(self, button_label: str):
        super().__init__()
        self.setText(button_label)
        self.setProperty("class", "power-btn")


class PowerWidgetMenu(QMenu):
    def __init__(self, backGroundColor="282a36", backGroundAccent="121b21", itemAmount=3, itemHeight=20):
        super().__init__()
        self.setMinimumSize(150,  itemHeight * itemAmount)
        self.radius = 8
        self.setStyleSheet('''
            QMenu {{
                background: #{backGroundColor};
                border-radius: {radius}px;
                margin-top: 5px;
                margin-right: 6px;
                text-align: center;
                padding: 10px;
            }}
            QMenu::item {{
                color: white;
                font-size: 16px;
                padding: 10px;
                height: 20px;
                font-family: 'Hack Nerd Font', 'Bars', 'Font Awesome 5 Free Regular';
            }}
            QMenu::item:selected {{
                background: #{backGroundAccent};
                border-radius: {radius}px;
            }}
        '''.format(backGroundColor=backGroundColor, backGroundAccent=backGroundAccent, radius=self.radius))

    def resizeEvent(self, event):
        path = QtGui.QPainterPath()
        # the rectangle must be translated and adjusted by 1 pixel in order to
        # correctly map the rounded shape
        rect = QtCore.QRectF(self.rect()).adjusted(0, 5.5, -6, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)
        # QRegion is bitmap based, so the returned QPolygonF (which uses float
        # values must be transformed to an integer based QPolygon
        region = QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon())
        self.setMask(region)


class PowerButtonsWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            layout: list[str]
    ):
        super().__init__(0, class_name="power-buttons-widget")
        self._menu = PowerWidgetMenu()
        self._menu.setProperty("class", "power-button-menu")

        power_component_builders = {
            "shutDown": self._build_shut_down_action,
            "restart": self._build_restart_action,
            "lock": self._build_lock_action
        }

        for components in layout:
            power_component_builders[components]()

        self._button = PowerWidgetButton(label)
        self._button.setMenu(self._menu)
        self.widget_layout.addWidget(self._button)

    def _build_shut_down_action(self):
        self._menu.addAction("\udb81\udc25 Shut Down", self._shut_down_action)

    def _build_restart_action(self):
        self._menu.addAction("\uead2 Restart", self._restart_action)

    def _build_lock_action(self):
        self._menu.addAction("\uf456 Lock", self._lock_action)

    def _shut_down_action(self):
        subprocess.Popen("shutdown /s /t 0", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        print("Action one clicked!")

    def _restart_action(self):
        subprocess.Popen("shutdown /r /t 0", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        print("Action one clicked!")

    def _lock_action(self):
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        print("Action one clicked!")
