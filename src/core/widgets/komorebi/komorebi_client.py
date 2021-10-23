import subprocess
import json
from typing import Optional


class KomorebiClient:
    def __init__(
            self,
            komorebic_path: str = "komorebic.exe",
            timeout_secs: int = 1
    ):
        super().__init__()
        self.timeout_secs = timeout_secs
        self.komorebic_path: str = komorebic_path
        self.state = None
        self.update_state()

    def _log_error(self, exception: Exception, msg: str = None):
        print(f"{self.komorebic_path} : {msg}", exception)

    def update_state(self) -> Optional[dict]:
        self.state = None

        try:
            proc = subprocess.Popen([self.komorebic_path, "state"],  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            stdout, stderr = proc.communicate(timeout=self.timeout_secs)
            try:
                self.state = json.loads(stdout)
            except json.JSONDecodeError:
                # self._log_error(e, "Failed to decode komorebi state from JSON")
                pass
        except subprocess.SubprocessError as e:
            self._log_error(e, "Failed to retrieve komorebi state")

        return self.state

    def get_focused_workspace_idx(self, screen_idx: int):
        try:
            return self.state['monitors']['elements'][screen_idx]['workspaces']['focused']
        except KeyError as e:
            self._log_error(e, "Failed to get focused workspace from komorebi state")
        except IndexError as e:
            self._log_error(e, f"Failed to get focused workspace for screen at index {screen_idx}")

    def get_workspaces(self, screen_idx: int) -> list:
        try:
            return self.state['monitors']['elements'][screen_idx]['workspaces']['elements']
        except Exception as e:
            self._log_error(e, f"Failed to retrieve workspaces for screen {screen_idx}")
            return []

    def get_workspace(self, screen_idx: int, ws_idx: int) -> Optional[dict]:
        try:
            workspaces = self.get_workspaces(screen_idx)
            return workspaces[ws_idx]
        except Exception as e:
            self._log_error(e, f"Failed to get focused workspace for screen at index {screen_idx}")

    def get_workspace_num_windows(self, screen_idx: int, ws_idx: int) -> Optional[int]:
        try:
            workspace = self.get_workspace(screen_idx, ws_idx)
            containers = workspace['containers']['elements']
            num_tiled_windows = sum([len(cont['windows']['elements']) if 'windows' in cont else 0 for cont in containers])
            num_float_windows = len(workspace['floating_windows'])
            return num_tiled_windows + num_float_windows
        except Exception as e:
            self._log_error(e, f"Failed to retrieve number of windows for workspace at index {ws_idx}")

    def activate_workspace(self, ws_idx: int) -> None:
        try:
            subprocess.Popen([self.komorebic_path, "focus-workspace", str(ws_idx)])
        except Exception as e:
            self._log_error(e, f"Failed to focus workspace at index {ws_idx}")

    def next_workspace(self) -> None:
        try:
            subprocess.Popen([self.komorebic_path, "cycle-workspace", "next"])
        except subprocess.SubprocessError as e:
            self._log_error(e, "Failed to cycle komorebi workspace")

    def prev_workspace(self) -> None:
        try:
            subprocess.Popen([self.komorebic_path, "cycle-workspace", "prev"])
        except subprocess.SubprocessError as e:
            self._log_error(e, "Failed to cycle komorebi workspace")

    def toggle_focus_mouse(self) -> None:
        try:
            subprocess.Popen([self.komorebic_path, "toggle-focus-follows-mouse"])
        except subprocess.SubprocessError as e:
            self._log_error(e, "Failed to toggle focus-follows-mouse")
