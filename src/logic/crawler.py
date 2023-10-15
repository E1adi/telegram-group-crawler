import asyncio
from asyncio_pool import AioPool
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel, User
from telethon.utils import get_input_channel
from .channel_cache import ChannelCache
from .message_matchers import IMessageMatcher
from .message_matchers import ForwardedMessagesMessageMatcher
from .message_matchers import UrlChannelLinkMessageMatcher
from .message_matchers import TextUrlChannelLinkMessageMatcher
from datetime import datetime
from typing import List, Set, Dict, Optional, Coroutine, AsyncIterable, Tuple
from .utils import get_channel_link


class Crawler:
    _DATETIME_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"

    def __init__(self, app_name, api_id, api_hash):
        self._client = TelegramClient(app_name, api_id, api_hash)
        self.channel_cache = ChannelCache()
        self._matchers: List[IMessageMatcher] = [
            ForwardedMessagesMessageMatcher(),
            TextUrlChannelLinkMessageMatcher(),
            UrlChannelLinkMessageMatcher()
        ]

    def async_one_time_init(self) -> Coroutine[any, any, TelegramClient] | TelegramClient:
        return self._client.start()

    async def _init_groups(self, groups_to_crawl: []) -> (Set[int], Dict[int, str]):
        temp_working_set = {c: await self._get_entity(c) for c in groups_to_crawl}
        ids_to_links = {value.id: key for (key, value) in temp_working_set.items() if value is not None}
        to_do = set(ids_to_links.keys())
        return to_do, ids_to_links

    async def test_client(self):
        me = await self._client.get_me()
        print(me.stringify())

    async def start(self,
                    groups: List[str],
                    since_stamp: Optional[datetime] = None,
                    concurrency_level: Optional[int] = None) -> AsyncIterable[Tuple[int, Set[int], Set[int], Dict[int, str]]]:
        (to_do, ids_to_links_map) = await self._init_groups(groups)
        done: Set[int] = set()
        pool = AioPool(concurrency_level) if concurrency_level is not None else AioPool()
        iteration = 1
        while len(to_do) > 0:
            handle_tasks = [self._handle_channel(c, since_stamp) for c in to_do.copy()]
            results = await pool.map(lambda task: task, handle_tasks)
            for (current, referenced) in results:
                if current is not None:
                    for ref in referenced:
                        if current.id != ref.id and ref.id not in ids_to_links_map.keys():
                            to_do.add(ref.id)
                            ids_to_links_map.update({ref.id: get_channel_link(ref)})
                    to_do.remove(current.id)
                    done.add(current.id)

            yield iteration, to_do.copy(), done.copy(), ids_to_links_map.copy()
            iteration = iteration + 1

    async def _handle_channel(self, channel_id: str | int, since_stamp: datetime) -> \
            (Optional[Channel], Optional[List[Channel]]):
        try:
            channel = await self._get_entity(channel_id)
            if channel is None:
                return None, None

            await self._join_channel(channel)

            return (channel, await self._get_referenced_channels(channel, since_stamp)) \
                if channel is not None \
                else None

        except TypeError as type_error:
            print(f'[--@]: TypeError exception. Channel type: {type(channel)} got for id: {channel_id}. {type_error}')
            return None, None
        except Exception as ex:
            print(f'[--@]: Exception of type {type(ex)} rose while trying to handle channel id:{channel_id}, {ex}')
            return None, None

    async def _join_channel(self, channel: Channel):
        try:
            await self._join_normal_channel(channel)
        except ChannelPrivateError:
            await self._join_private_channel(channel.username)

    async def _get_entity(self, channel_id: str | int, is_second_try: bool = False) -> Optional[Channel]:
        cached = self.channel_cache[channel_id]
        if cached is not None:
            return cached

        # noinspection SpellCheckingInspection
        if isinstance(channel_id, str) and '/joinchat/' in channel_id:
            await self._join_private_channel(channel_id)
        try:
            result = await self._client.get_entity(channel_id)
            if result is not None and isinstance(result, Channel):
                self.channel_cache.add(result)
                return result
            else:
                return None

        except ValueError:
            return None
        except ChannelPrivateError:
            if is_second_try:
                return None

            await self._join_private_channel(channel_id)
            return await self._get_entity(channel_id, is_second_try=True)
        except FloodWaitError as flood_wait_error:
            print (f"Reached API rate limit. Sleeping for {flood_wait_error.seconds} seconds")
            await asyncio.sleep(flood_wait_error.seconds)
            return await self._get_entity(channel_id)
        except Exception as ex:
            print(f'[--@]: {type(ex)} rose while trying to resolve channel id:{channel_id}, {ex}')
            return None

    async def _get_referenced_channels(self, channel: Channel, since_stamp: Optional[datetime] = None) -> List[Channel]:
        ids: Set[str | int] = set()
        async for msg in self._client.iter_messages(channel, limit=None, offset_date=since_stamp, reverse=True):
            for matcher in self._matchers:
                if matcher.match(msg):
                    new_ids = matcher.extract_ids(msg)
                    ids.update(new_ids)

        entity_generator = (await self._get_entity(channel_id) for channel_id in ids)
        return [c async for c in entity_generator if c is not None and not isinstance(c, User)]

    def _join_normal_channel(self, channel: Channel) -> Coroutine:
        return self._client(JoinChannelRequest(get_input_channel(channel)))

    def _join_private_channel(self, channel_username: str) -> Coroutine:
        return self._client(ImportChatInviteRequest(channel_username))

    def __del__(self):
        self._client.disconnect()


