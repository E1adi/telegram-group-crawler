from .message_matcher_interface import IMessageMatcher
from telethon.tl.types import Message


class ForwardedMessagesMessageMatcher(IMessageMatcher):
    def match(self, message: Message):
        return message.fwd_from is not None and message.fwd_from.from_id.channel_id != message.peer_id.channel_id

    def extract_ids(self, message: Message):
        return {message.fwd_from.from_id.channel_id}
