import asyncio
import json
import typer
from typing_extensions import Annotated
from pathlib import Path
from .help_consts import HelpDocs
from typing import List, Optional, TypeVar
from src.driver import Driver, TelegramCreds
from datetime import datetime
from dateutil import relativedelta
from pprint import pprint
T = TypeVar("T")


def load_json_file(path: Path, type_hint:T) -> T:
    if not path.exists() or not path.is_file():
        raise ValueError("Creds file does not exists")
    with open(path, 'r') as input_stream:
        return json.load(input_stream, object_hook=lambda obj: type_hint(**obj))


async def async_cli(
    telegram_creds_file: Path,
    telegram_groups: Optional[List[str]],
    telegram_groups_file: Optional[Path],
    history_period: Optional[int],
    crawling_depth: Optional[int],
    concurrency_limit: Optional[int],
    output_file_path: Optional[Path]
):
    creds = load_json_file(telegram_creds_file, TelegramCreds)
    groups = load_json_file(telegram_groups_file, List[str]) if telegram_groups_file is not None else []
    if telegram_groups is not None:
        groups.extend(telegram_groups)

    search_period = datetime.utcnow() - relativedelta.relativedelta(days=history_period) \
        if history_period is not None else None

    driver = Driver(creds,
                    history_period=search_period,
                    crawling_depth=crawling_depth,
                    concurrency_limit=concurrency_limit,
                    output_file=output_file_path)

    await driver.async_one_time_init()

    async for (iteration, to_do, done, ids_to_link_map) in driver.start(groups):
        print(f'Iteration #{iteration}:')
        print('To-Do:')
        pprint(to_do)
        print('Done:')
        pprint(done)
        print('IdsToLinks')
        pprint(ids_to_link_map)


    print("Done!!!!")


def cli(
        telegram_creds_file: Annotated[Path, typer.Option(..., '--creds', '-c', help=HelpDocs.telegram_creds_file)],
        telegram_groups: Annotated[Optional[List[str]], typer.Option('--group', '-g', help=HelpDocs.telegram_group)] = [],
        telegram_groups_file: Annotated[Optional[Path], typer.Option('--groups-file', help=HelpDocs.telegram_groups_file)] = None,
        history_period: Annotated[Optional[int], typer.Option('--history-period', '-p', help=HelpDocs.history_period, min=0)] = None,
        crawling_depth: Annotated[Optional[int], typer.Option('--crawling-depth', '-d', help=HelpDocs.crawling_depth, min=0)] = None,
        concurrency_limit: Annotated[Optional[int], typer.Option('--concurrency-limit', '-l', help=HelpDocs.concurrency_limit, min=1)] = None,
        output_file_path: Annotated[Optional[Path], typer.Option('--output', '-o', help=HelpDocs.output_file_path)] = None
    ):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_cli(
        telegram_creds_file,
        telegram_groups,
        telegram_groups_file,
        history_period,
        crawling_depth,
        concurrency_limit,
        output_file_path)
    )

