from message_filters.message_filter_interface import ReferencedChannelMessageFilter
from telethon.tl.types import Message


class ForwardedMessagesMessageFilter(ReferencedChannelMessageFilter):
    def filter(self, message: Message):
        return (message.fwd_from != None and message.fwd_from.from_id.channel_id != message.peer_id.channel_id)

    def extract_ids(self, message: Message):
        return { message.fwd_from.from_id.channel_id }