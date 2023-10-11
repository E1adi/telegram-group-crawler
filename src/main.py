from datetime import datetime
from dateutil.relativedelta import relativedelta
from crawler import Crawler
import asyncio
from pprint import pprint

APP_NAME = 'Your app name'
API_ID = 'Your api ID'
API_HASH = 'Your api hash'
GROUPS_TO_CRAWL_FROM = ['group id (link or id as number)']

async def main():
    crawler = await Crawler.create(APP_NAME, API_ID, API_HASH, GROUPS_TO_CRAWL_FROM)
    await crawler.test_client() # Test the TelegramClient connection

    async for (iter, to_do, done, ids_to_link_map) in (
            crawler.start(since_stamp=datetime.utcnow() - relativedelta(days=3))):
        print(f'Iteration #{iter}:')
        print('To-Do:')
        pprint(to_do)
        print('Done:')
        pprint(done)
        print('IdsToLinks')
        pprint(ids_to_link_map)

    print("Done!!!!")

    print('')
    print('')
    print('')
    print('')

    pprint(crawler.get_results())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
