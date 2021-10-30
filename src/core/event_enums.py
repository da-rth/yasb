from enum import Enum, EnumMeta


class MetaEvent(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class Event(Enum, metaclass=MetaEvent):
    pass


class KomorebiEvent(Event):
    KomorebiConnect = "KomorebiConnect"
    KomorebiUpdate = "KomorebiUpdate"
    KomorebiDisconnect = "KomorebiDisconnect"
    FocusWorkspaceNumber = "FocusWorkspaceNumber"
    FocusChange = "FocusChange"


class BarEvent(Event):
    CloseBar = "CloseBar"
    ReloadBars = "ReloadBars"
