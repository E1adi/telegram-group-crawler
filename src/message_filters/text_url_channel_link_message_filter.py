from telethon.tl.types import MessageEntityTextUrl
from message_filters.message_filter_interface import ReferencedChannelMessageFilter, Message
from message_filters.common import extract_telegram_channel_link
from py_linq import Enumerable

class TextUrlChannelLinkMessageFilter(ReferencedChannelMessageFilter):
    def filter(self, message: Message):
        return (message.entities is not None and
                any((TextUrlChannelLinkMessageFilter._combined_entity_checks(e) for e in message.entities)))

    def extract_ids(self, message: Message):
        relevant_entities = Enumerable([extract_telegram_channel_link(e.url) for e in message.entities if TextUrlChannelLinkMessageFilter._combined_entity_checks(e)])
        return set(relevant_entities.select_many(lambda l: l).to_list())


    @classmethod
    def _combined_entity_checks(cls, entity):
        return (TextUrlChannelLinkMessageFilter.is_text_url_entity(entity) and entity.url is not None and
                len(extract_telegram_channel_link(entity.url)) > 0)

    @classmethod
    def is_text_url_entity(cls, entity):
        return isinstance(entity, MessageEntityTextUrl)

