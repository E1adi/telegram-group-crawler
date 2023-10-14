import asyncio

import telethon.utils
from asyncio_pool import AioPool
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel, User
from telethon.utils import get_input_channel
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

    async def start(self, since_stamp: datetime = None, concurrency_level: int = None):
        pool = AioPool(concurrency_level)
        iteration = 0
        while len(self._to_do) > 0:
            handle_tasks = [self._handle_channel(c, since_stamp) for c in self._to_do.copy()]
            results = await pool.map(lambda task: task, handle_tasks)
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

    def dump_results_to_file(self, path: str):
        results = self.get_results()
        gl_json = json.dumps(results)
        with open(path, 'wb') as output:
            output.write(gl_json.encode())

    async def _handle_channel(self, id: str | int, since_stamp: datetime) -> (Channel | None, list[Channel] | None):
        try:
            channel = await self._get_entity(id)
            if channel is None:
                return (None, None)

            await self._join_channel(channel)

            return (channel, await self._get_referenced_channels(channel, since_stamp)) \
                if channel is not None \
                else None

        except TypeError as type_error:
            print(f'@@@@@@@@@@@@@@@@@@@@ TypeError exception. Channel type: {type(channel)} got for id: {id}. {type_error}')
            return (None, None)
        except Exception as ex:
            print(f'@@@@@@@@@@@@@@@@@@@@ Exception of type {type(ex)} rose while trying to handle channel id:{id}, {ex}')
            return (None, None)

    async def _join_channel(self, channel: Channel):
        try:
            await self._join_normal_channel(channel)
        except ChannelPrivateError:
            await self._join_private_channel(channel.username)

    async def _get_entity(self, id: str | int, is_second_try: bool = False):
        if isinstance(id, str) and '/joinchat/' in id:
            await self._join_private_channel(id)
        try:
            return await self._client.get_entity(id)
        except ValueError:
            return None
        except ChannelPrivateError:
            if is_second_try:
                return None

            await self._join_private_channel(id)
            return await self._get_entity(id, is_second_try=True)
        except FloodWaitError as flood_wait_error:
            print (f"Reached API rate limit. Sleeping for {flood_wait_error.seconds} seconds")
            await asyncio.sleep(flood_wait_error.seconds * 1000)
            return await self._get_entity(id)
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

        return [c async for c in (await self._get_entity(id) for id in ids) if c is not None and not isinstance(c, User) ]

    def _join_normal_channel(self, channel: Channel):
        return self._client(JoinChannelRequest(get_input_channel(channel)))

    def _join_private_channel(self, channel_username: str):
        return self._client(ImportChatInviteRequest(channel_username))

    def get_results(self) -> list[str]:
        return list(self._ids_to_links.values())

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