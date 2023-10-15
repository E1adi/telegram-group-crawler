from telethon.tl.types import MessageEntityUrl
from .message_matcher_interface import IMessageMatcher, Message
from .common import extract_telegram_channel_link


class UrlChannelLinkMessageMatcher(IMessageMatcher):
    def match(self, message: Message):
        return (message.entities is not None and
                any((UrlChannelLinkMessageMatcher.is_url_entity(e) for e in message.entities)))

    def extract_ids(self, message: Message):
        return extract_telegram_channel_link(message.message)

    @classmethod
    def is_url_entity(cls, entity):
        return isinstance(entity, MessageEntityUrl)

