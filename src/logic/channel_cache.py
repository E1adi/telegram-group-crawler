from typing import Dict, Optional
from telethon.tl.types import Channel
from .utils import get_channel_link


class ChannelCache:
    def __init__(self):
        self._ids_to_channels: Dict[int, Channel] = {}
        self._links_to_channels: Dict[str, Channel] = {}

    def add(self, channel: Channel):
        channel_id = channel.id
        if channel_id in self._ids_to_channels:
            return

        link = get_channel_link(channel)
        self._ids_to_channels[channel_id] = channel
        self._links_to_channels[link] = channel

    def get(self, channel_identifier: int | str) -> Optional[Channel]:
        if channel_identifier is None:
            return None

        selected_dict = self._ids_to_channels if isinstance(channel_identifier, int) else self._links_to_channels
        return selected_dict[channel_identifier] if channel_identifier in selected_dict else None

    def __getitem__(self, item: str | int):
        return self.get(item)
