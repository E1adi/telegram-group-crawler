from src.logic.crawler import Crawler
from typing import List, Type, Optional, Coroutine, AsyncIterable, Set, Dict, Tuple
from datetime import datetime
from pathlib import Path
import json


class TelegramCreds:
    def __init__(self, app_name: str, api_id: str, api_hash: str):
        self.app_name = app_name
        self.api_id = api_id
        self.api_hash = api_hash


class Driver:
    def __init__(
            self,
            creds: TelegramCreds | Type[TelegramCreds],
            history_period: Optional[datetime],
            crawling_depth: Optional[int],
            concurrency_limit: Optional[int],
            output_file: Optional[Path]
    ):
        self._crawler: Crawler = Crawler(creds.app_name, creds.api_id, creds.api_hash)
        self._history_period: Optional[datetime] = history_period
        self._crawling_depth: Optional[int] = crawling_depth
        self._concurrency_limit: Optional[int] = concurrency_limit
        self._output_file: Optional[Path] = output_file
        if self._output_file is not None and self._output_file.is_dir():
            raise ValueError("Output path is a directory")

    def test_client_connection(self) -> Coroutine:
        return self._crawler.test_client()  # Test the TelegramClient connection

    def async_one_time_init(self) -> Coroutine:
        return self._crawler.async_one_time_init()

    async def start(self, groups: List[str]) -> AsyncIterable[Tuple[int, Set[int], Set[int], Dict[int, str]]]:
        async for (iteration, to_do, done, ids_to_links_map) in self._crawler.start(groups,
                                                                                    since_stamp=self._history_period,
                                                                                    concurrency_level=self._concurrency_limit):
            yield iteration, to_do, done, ids_to_links_map
            if iteration == self._crawling_depth:
                if self._output_file is not None:
                    list_results = [ids_to_links_map[group_id] for group_id in done]
                    Driver.dump_to_file(list_results, self._output_file)

                break

    @classmethod
    def dump_to_file(cls, results: List[str], path: Path):
        gl_json = json.dumps(results)
        with open(path, 'wb') as output:
            output.write(gl_json.encode())
