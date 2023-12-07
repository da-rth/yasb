import subprocess
import logging
import json
from contextlib import suppress
from typing import Optional


def add_index(dictionary: dict, dictionary_index: int) -> dict:
    dictionary['index'] = dictionary_index
    return dictionary


class KomorebiClient:
    def __init__(
            self,
            komorebic_path: str = "komorebic.exe",
            timeout_secs: float = 0.5
    ):
        super().__init__()
        self._timeout_secs = timeout_secs
        self._komorebic_path = komorebic_path
        self._previous_poll_offline = False
        self._previous_mouse_follows_focus = False

    def query_state(self) -> Optional[dict]:
        with suppress(json.JSONDecodeError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            output = subprocess.check_output([self._komorebic_path, "state"], timeout=self._timeout_secs, shell=True)
            return json.loads(output)

    def get_screens(self, state: dict) -> list:
        return state['monitors']['elements']

    def get_screen_by_hwnd(self, state: dict, screen_hwnd: int) -> Optional[dict]:
        for i, screen in enumerate(self.get_screens(state)):
            if screen.get('id', None) == screen_hwnd:
                return add_index(screen, i)

    def get_workspaces(self, screen: dict) -> list:
        return [add_index(workspace, i) for i, workspace in enumerate(screen['workspaces']['elements'])]

    def get_workspace_by_index(self, screen: dict, workspace_index: int) -> Optional[dict]:
        try:
            return self.get_workspaces(screen)[workspace_index]
        except IndexError:
            return None

    def get_focused_workspace(self, screen: dict) -> Optional[dict]:
        try:
            focused_workspace_index = screen['workspaces']['focused']
            focused_workspace = self.get_workspace_by_index(screen, focused_workspace_index)
            focused_workspace['index'] = focused_workspace_index
            return focused_workspace
        except (KeyError, TypeError):
            return None

    def get_num_windows(self, workspace: dict):
        containers = workspace['containers']['elements']
        if workspace.get('floating_windows', []):
            return True

        for container in containers:
            if container.get('windows', {}).get('elements', []):
                return True

        return False

    def get_workspace_by_window_hwnd(self, workspaces: list[Optional[dict]], window_hwnd: int) -> Optional[dict]:
        for i, workspace in enumerate(workspaces):

            for floating_window in workspace['floating_windows']:
                if floating_window['hwnd'] == window_hwnd:
                    return add_index(workspace, i)

            if ('containers' not in workspace) or ('elements' not in workspace['containers']):
                continue

            for container in workspace['containers']['elements']:
                if ('windows' not in container) or ('elements' not in container['windows']):
                    continue

                for managed_window in container['windows']['elements']:
                    if managed_window['hwnd'] == window_hwnd:
                        return add_index(workspace, i)

    def get_mouse_follows_focus(self, state: dict) -> bool:
        return state['mouse_follows_focus']

    def activate_workspace(self, ws_idx: int, wait: bool = False) -> None:
        p = subprocess.Popen([self._komorebic_path, "focus-workspace", str(ws_idx)], shell=True)

        if wait:
            p.wait()

    def hide_preview(self, ws_idx: int, stay_on_workspace: bool = False) -> None:
        if self._previous_mouse_follows_focus:
            self._previous_mouse_follows_focus = False
            self.toggle("mouse-follows-focus", True)

        if not stay_on_workspace:
            self.activate_workspace(ws_idx, True)

    def preview_workspace(self, ws_idx: int, state: dict) -> None:
        is_mff_active = self.get_mouse_follows_focus(state)

        if is_mff_active and not self._previous_mouse_follows_focus:
            self._previous_mouse_follows_focus = True
            self.toggle("mouse-follows-focus", True)

        self.activate_workspace(ws_idx, True)

    def next_workspace(self) -> None:
        try:
            subprocess.Popen([self._komorebic_path, "cycle-workspace", "next"], shell=True)
        except subprocess.SubprocessError:
            logging.exception("Failed to cycle komorebi workspace")

    def prev_workspace(self) -> None:
        try:
            subprocess.Popen([self._komorebic_path, "cycle-workspace", "prev"], shell=True)
        except subprocess.SubprocessError:
            logging.exception("Failed to cycle komorebi workspace")

    def toggle_focus_mouse(self) -> None:
        try:
            subprocess.Popen([self._komorebic_path, "toggle-focus-follows-mouse"], shell=True)
        except subprocess.SubprocessError:
            logging.exception("Failed to toggle focus-follows-mouse")

    def change_layout(self, layout: str) -> None:
        try:
            subprocess.Popen([self._komorebic_path, "change-layout", layout], shell=True)
        except subprocess.SubprocessError:
            logging.exception(f"Failed to change layout of currently active workspace to {layout}")

    def flip_layout(self) -> None:
        try:
            subprocess.Popen(
                [self._komorebic_path, "flip-layout"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            )
        except subprocess.SubprocessError:
            pass

    def toggle(self, toggle_type: str, wait: bool = False) -> None:
        try:
            p = subprocess.Popen([self._komorebic_path, f"toggle-{toggle_type}"], shell=True)

            if wait:
                p.wait()
        except subprocess.SubprocessError:
            logging.exception(f"Failed to toggle {toggle_type} for currently active workspace")

    def wait_until_subscribed_to_pipe(self, pipe_name: str):
        proc = subprocess.Popen(
            [self._komorebic_path, "subscribe", pipe_name],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _stdout, stderr = proc.communicate()

        return stderr, proc
