import asyncio
from itertools import cycle, islice
from core.widgets.base import BaseWidget
from core.validation.widgets.win32.media_player import VALIDATION_SCHEMA
from core.utils.win32 import media_control
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QCursor


class MediaWidgetButton(QPushButton):
    def __init__(self, button_type: str, button_label: str):
        super().__init__()
        self.button_type = button_type
        self.setText(button_label)
        self.setProperty("class", f"media-btn {button_type}")

    def set_active(self, is_active: bool):
        if is_active:
            self.setProperty("class", f"media-btn {self.button_type} active")
        else:
            self.setProperty("class", f"media-btn {self.button_type}")

        self.setStyleSheet('')


async def call_async_callback(callback, *args):
    await callback(*args)


class MediaWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            update_interval: int,
            keep_thumbnail_aspect_ratio: bool,
            layout: list[str],
            icons: dict[str, str]
    ):
        super().__init__(update_interval, class_name="media-widget")
        self._icons = icons
        self._update_interval = update_interval
        self._keep_thumbnail_aspect_ratio = keep_thumbnail_aspect_ratio
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt
        self._playing_media = None
        self._shuffle = False
        self._repeat = False
        self._repeat_options = cycle([
            media_control.WindowsMediaRepeat.Off,
            media_control.WindowsMediaRepeat.Track,
            media_control.WindowsMediaRepeat.List
        ])

        self._play_pause_btn = None
        self._repeat_btn = None
        self._shuffle_btn = None
        self._next_btn = None
        self._prev_btn = None
        self._close_btn = None

        media_component_builders = {
            "label": self._build_label,
            "next": self._build_next_btn,
            "prev": self._build_prev_btn,
            "close": self._build_close_btn,
            "thumbnail": self._build_thumbnail,
            "shuffle": self._build_shuffle_btn,
            "repeat": self._build_repeat_btn,
            "play_pause": self._build_play_pause_btn
        }

        for media_component_type in layout:
            media_component_builders[media_component_type]()

        self.register_callback("update_label", self._update_label)
        self.register_callback("toggle_label", self._toggle_label)

        self.callback_timer = "update_label"
        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()

        self._update_label()

    async def _update_thumbnail(self, thumbnail_ref) -> None:
        if thumbnail_ref:
            wh = self.bar.dimensions['height']
            thumbnail_image = await media_control.stream_to_image(thumbnail_ref)
            self._thumbnail_pixmap = QPixmap.fromImage(thumbnail_image)
            self._thumbnail.setPixmap(self._thumbnail_pixmap.scaled(wh, wh, self._thumbnail_aspect_ratio))

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        media_info = asyncio.run(media_control.get_media_info())
        playback_info = asyncio.run(media_control.get_playback_info())

        title_artist = f"{media_info['title']} - {media_info['artist']}"

        playback_controls = playback_info['controls']
        is_play_enabled = playback_controls.get('is_play_enabled', False)

        if self._playing_media != title_artist and self.bar:
            if self._thumbnail:
                asyncio.run(self._update_thumbnail(media_info['thumbnail']))
            self._playing_media = title_artist
            self.show()

        if self._play_pause_btn:
            if is_play_enabled:
                self._play_pause_btn.setText(self._icons["play"])
            else:
                self._play_pause_btn.setText(self._icons["pause"])

        if self._shuffle_btn:
            self._shuffle = playback_info.get('is_shuffle_active', False)
            self._update_shuffle_btn_label()

        if self._repeat_btn:
            repeat_cycle_mode = playback_info.get('auto_repeat_mode', 0)
            repeat_cycle_mode = repeat_cycle_mode if repeat_cycle_mode else 0
            islice(self._repeat_options, repeat_cycle_mode, None)
            self._repeat = media_control.WindowsMediaRepeat(repeat_cycle_mode)
            self._update_repeat_btn_label()

        try:
            active_label.setText(active_label_content.format(media=media_info, playback=playback_info))
        except KeyError:
            active_label.setText(active_label_content)
        except TypeError:
            active_label.setText("No media playing")

    def _update_repeat_btn_label(self):
        if self._repeat == media_control.WindowsMediaRepeat.Off:
            self._repeat_btn.setText(self._icons["repeat_off"])
            self._repeat_btn.set_active(False)
        elif self._repeat == media_control.WindowsMediaRepeat.Track:
            self._repeat_btn.setText(self._icons["repeat_track"])
            self._repeat_btn.set_active(True)
        else:
            self._repeat_btn.setText(self._icons["repeat_list"])
            self._repeat_btn.set_active(True)

    def _update_shuffle_btn_label(self):
        self._shuffle_btn.set_active(self._shuffle)

    def _build_label(self):
        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label.mousePressEvent = lambda _e: self._toggle_label()
        self._label_alt.setProperty("class", "label alt")
        self._label_alt.mousePressEvent = lambda _e: self._toggle_label()
        self._label_alt.hide()
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

    def _preview_thumbnail(self):
        if self._thumbnail_preview.isVisible():
            self._thumbnail_preview.hide()
        else:
            cursor = QCursor()

            self._thumbnail_preview.setPixmap(self._thumbnail_pixmap)
            self._thumbnail_preview.show()

            x_pos = cursor.pos().x()
            y_pos = self.screen().geometry().y() + self.bar.dimensions['height'] \
                if self.bar.alignment['position'] == "top" \
                else (self.screen().geometry().y() +
                      self.screen().geometry().height() -
                      self._thumbnail_preview.height() -
                      self.bar.dimensions['height'])

            self._thumbnail_preview.setGeometry(
                x_pos,
                y_pos,
                self._thumbnail_preview.width(),
                self._thumbnail_preview.height()
            )
            self._thumbnail_preview.show()

    def _build_thumbnail(self):
        self._thumbnail_preview = QLabel()
        self._thumbnail_preview.setWindowFlag(Qt.WindowType.Tool)
        self._thumbnail_preview.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self._thumbnail_preview.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._thumbnail_preview.mousePressEvent = lambda _e: self._thumbnail_preview.hide()
        self._thumbnail_preview.hide()

        self._thumbnail = QLabel()
        self._thumbnail.setProperty("class", "thumbnail")
        self._thumbnail.mousePressEvent = lambda _e: self._preview_thumbnail()
        self._thumbnail_aspect_ratio = Qt.AspectRatioMode.KeepAspectRatio \
            if self._keep_thumbnail_aspect_ratio \
            else Qt.AspectRatioMode.IgnoreAspectRatio
        self.widget_layout.addWidget(self._thumbnail)

    def _build_close_btn(self):
        self._close_btn = MediaWidgetButton("close", self._icons["close"])
        self._close_btn.clicked.connect(lambda: self._handle_btn_press("close"))
        self.widget_layout.addWidget(self._close_btn)

    def _build_prev_btn(self):
        self._prev_btn = MediaWidgetButton("prev", self._icons["prev"])
        self._prev_btn.clicked.connect(lambda: self._handle_btn_press("prev"))
        self.widget_layout.addWidget(self._prev_btn)

    def _build_next_btn(self):
        self._next_btn = MediaWidgetButton("next", self._icons["next"])
        self._next_btn.clicked.connect(lambda: self._handle_btn_press("next"))
        self.widget_layout.addWidget(self._next_btn)

    def _build_play_pause_btn(self):
        self._play_pause_btn = MediaWidgetButton("play_pause", self._icons["play"])
        self._play_pause_btn.clicked.connect(lambda: self._handle_btn_press("play_pause"))
        self.widget_layout.addWidget(self._play_pause_btn)

    def _build_shuffle_btn(self):
        self._shuffle_btn = MediaWidgetButton("shuffle", self._icons["shuffle"])
        self._shuffle_btn.clicked.connect(lambda: self._handle_btn_press("shuffle"))
        self.widget_layout.addWidget(self._shuffle_btn)

    def _build_repeat_btn(self):
        self._repeat_btn = MediaWidgetButton("repeat", self._icons["repeat_off"])
        self._repeat_btn.clicked.connect(lambda: self._handle_btn_press("repeat"))
        self.widget_layout.addWidget(self._repeat_btn)

    def _handle_btn_press(self, btn_name):
        session = asyncio.run(media_control.get_current_session())
        callbacks = {
            "prev": session.try_skip_previous_async,
            "next": session.try_skip_next_async,
            "shuffle": session.try_change_shuffle_active_async,
            "play_pause": session.try_toggle_play_pause_async,
            "repeat": session.try_change_auto_repeat_mode_async
        }

        if btn_name == "close":
            self.hide()
        elif btn_name == "shuffle":
            self._shuffle = not self._shuffle
            self._update_shuffle_btn_label()
            asyncio.run(call_async_callback(callbacks[btn_name], self._shuffle))
        elif btn_name == "repeat":
            self._repeat = next(self._repeat_options)
            self._update_repeat_btn_label()
            asyncio.run(call_async_callback(callbacks[btn_name], self._repeat.value))
        else:
            asyncio.run(call_async_callback(callbacks[btn_name]))

        self._update_label()