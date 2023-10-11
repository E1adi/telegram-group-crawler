from src.message_filters.message_filter_interface import ReferencedChannelMessageFilter, Message
from telethon.tl.types import MessageEntityUrl
from src.message_filters.common import extract_telegram_channel_link

class UrlChannelLinkMessageFilter(ReferencedChannelMessageFilter):
    def filter(self, message: Message):
        return (message.entities is not None and
                any((UrlChannelLinkMessageFilter.is_url_entity(e) for e in message.entities)))

    def extract_ids(self, message: Message):
        return extract_telegram_channel_link(message.message)

    @classmethod
    def is_url_entity(cls, entity):
        return isinstance(entity, MessageEntityUrl)

