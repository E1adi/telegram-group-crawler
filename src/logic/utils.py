from telethon.tl.types import Channel


def get_channel_link(channel: Channel):
    return f't.me/{channel.username}'

