import asyncio
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel
from message_filters.message_filter_interface import ReferencedChannelMessageFilter
from message_filters.forwarded_messages_message_filter import ForwardedMessagesMessageFilter
from message_filters.url_channel_link_message_filter import UrlChannelLinkMessageFilter
from message_filters.text_url_channel_link_message_filter import TextUrlChannelLinkMessageFilter
from datetime import datetime
import json

class Crawler:
    _DATETIME_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"

    def __init__(self, app_name, api_id, api_hash):
        self._client = TelegramClient(app_name, api_id, api_hash)
        self._filters: list[ReferencedChannelMessageFilter] = [
            ForwardedMessagesMessageFilter(),
            TextUrlChannelLinkMessageFilter(),
            UrlChannelLinkMessageFilter()
        ]

    async def init(self, groups_to_crawl: []):
        await self._client.start()
        temp_working_set = { c: await self._get_entity(c) for c in groups_to_crawl }
        self._ids_to_links = { value.id: key for (key, value)  in temp_working_set.items() if value != None }
        self._to_do = set(self._ids_to_links.keys())
        self._done = set()
        self._edges = {}

    async def test_client(self):
        me = await self._client.get_me()
        print(me.stringify())

    async def start(self, since_stamp: datetime = None):
        now = datetime.utcnow()
        iteration = 0
        while len(self._to_do) > 0:
            handle_tasks = [self._handle_channel(c, since_stamp) for c in self._to_do.copy()]
            results = await asyncio.gather(*handle_tasks)
            for (current, referenced) in results:
                if current is not None:
                    for ref in referenced:
                        if(current.id != ref.id and ref.id not in self._ids_to_links.keys()):
                            self._to_do.add(ref.id)
                            self._ids_to_links.update({ref.id: Crawler.get_channel_link(ref)})
                    self._to_do.remove(current.id)
                    self._done.add(current.id)
            yield iteration, self._to_do.copy(), self._done.copy(), self._ids_to_links.copy()
            iteration = iteration + 1

        self._dump_to_output_file(now, since_stamp)

    def _dump_to_output_file(self, now: datetime, since_stamp: datetime | None):
        actual_since = since_stamp.strftime(Crawler._DATETIME_FORMAT) if since_stamp is not None else 'Begining_Of_Time'
        formatted_now = now.strftime(Crawler._DATETIME_FORMAT)
        group_list = list(self._ids_to_links.values())
        gl_json = json.dumps(group_list)
        with open(f'telegram_groups-{actual_since}-{formatted_now}.json', 'wb') as output:
            output.write(gl_json.encode())

    async def _handle_channel(self, id: str | int, since_stamp: datetime) -> (Channel | None, list[Channel] | None):
        try:
            channel = await self._get_entity(id)
            await self._join_channel(channel.username)

            return (channel, await self._get_referenced_channels(channel, since_stamp)) \
                if channel is not None \
                else None

        except Exception as ex:
            print(f'@@@@@@@@@@@@@@@@@@@@ Exception raised: {ex}')
            return (None, None)

    async def _join_channel(self, channel_username: str):
        try:
            await self._client(JoinChannelRequest(channel_username))
        except ChannelPrivateError:
            await self._client(ImportChatInviteRequest(channel_username))

    async def _get_entity(self, id: str | int):
        try:
            return await self._client.get_entity(id)
        except ValueError:
            return None
        except Exception as ex:
            print(f'@@@@@@@@@@@@@@@@@@@@ Exception of type {type(ex)} rose while trying to resolve channel id:{id}, {ex}')
            return None

    async def _get_referenced_channels(self, channel, since_stamp = None) -> list[Channel]:
        ids: set[str | int] = set()
        messages = (m async for m in self._client.iter_messages(channel, limit=None, offset_date=since_stamp, reverse=True)
                    if any(f.filter(m) for f in self._filters))
        async for m in messages:
            for filter in self._filters:
                if filter.filter(m):
                    new_ids = filter.extract_ids(m)
                    ids.update(new_ids)

        return [c async for c in (await self._get_entity(id) for id in ids) if c is not None]

    def __del__(self):
        self._client.disconnect()

    @classmethod
    async def create(cls, app_name, api_id, api_hash, groups_to_crawl):
        self = Crawler(app_name, api_id, api_hash)
        await self.init(groups_to_crawl)
        return self

    @classmethod
    def get_channel_link(cls, channel: Channel):
        return f't.me/{channel.username}'