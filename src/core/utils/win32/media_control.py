from contextlib import suppress
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions


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


async def get_media_info():
    current_session = await get_current_session()

    if current_session:
        media_props = await current_session.try_get_media_properties_async()
        return {
            song_attr: media_props.__getattribute__(song_attr)
            for song_attr in dir(media_props)
            if song_attr[0] != '_'
        }


async def read_stream_into_buffer(thumbnail_ref) -> bytearray:
    buffer = Buffer(5000000)
    readable_stream = await thumbnail_ref.open_read_async()
    readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
    buffer_reader = DataReader.from_buffer(buffer)
    thumbnail_buffer = buffer_reader.read_bytes(buffer.length)
    return bytearray(thumbnail_buffer)
