from enum import Enum
from PyQt6.QtGui import QImage
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions

THUMBNAIL_BUFFER_SIZE = 5 * 1024 * 1024


class WindowsMediaRepeat(Enum):
    Off = 0
    Track = 1
    List = 2


async def get_current_session():
    """
    current_session.try_play_async()
    current_session.try_pause_async()
    current_session.try_toggle_play_pause()
    current_session.try_change_shuffle_active()
    current_session.try_skip_next()
    current_session.try_skip_previous()
    current_session.try_stop()
    """
    sessions = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    return sessions.get_current_session()


def props_to_dict(props):
    return {
        attr: props.__getattribute__(attr) for attr in dir(props) if attr[0] != '_'
    }


async def get_media_info():
    """
    {
        'album_artist': '',
        'album_title': '',
        'album_track_count': 0,
        'artist': 'Some Artist',
        'playback_type': 1,
        'subtitle': '',
        'thumbnail': <_winrt_Windows_Storage_Streams.IRandomAccessStreamReference>,
        'title': 'Some Title',
        'track_number': 0
    }
    """
    current_session = await get_current_session()

    if current_session:
        media_props = await current_session.try_get_media_properties_async()
        media_props = props_to_dict(media_props)
        del media_props['genres']
        return media_props


async def get_playback_info():
    """
    {
        'auto_repeat_mode': None,
        'controls': {
            'is_channel_down_enabled': False,
            'is_channel_up_enabled': False,
            'is_fast_forward_enabled': False,
            'is_next_enabled': False,
            'is_pause_enabled': False,
            'is_play_enabled': True,
            'is_play_pause_toggle_enabled': True,
            'is_playback_position_enabled': False,
            'is_playback_rate_enabled': False,
            'is_previous_enabled': False,
            'is_record_enabled': False,
            'is_repeat_enabled': False,
            'is_rewind_enabled': False,
            'is_shuffle_enabled': False,
            'is_stop_enabled': True
        },
        'is_shuffle_active': None,
        'playback_rate': None,
        'playback_status': 5,
        'playback_type': 1
    }
    """
    current_session = await get_current_session()

    if current_session:
        playback_props = current_session.get_playback_info()
        playback_props = props_to_dict(playback_props)
        playback_props['controls'] = props_to_dict(playback_props['controls'])
        return playback_props


async def stream_to_image(thumbnail_ref) -> QImage:
    buffer = Buffer(THUMBNAIL_BUFFER_SIZE)
    readable_stream = await thumbnail_ref.open_read_async()
    await readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
    buffer_reader = DataReader.from_buffer(buffer)
    thumbnail_buffer = buffer_reader.read_bytes(buffer.length)
    thumbnail_image = QImage()
    thumbnail_image.loadFromData(bytearray(thumbnail_buffer))
    return thumbnail_image
