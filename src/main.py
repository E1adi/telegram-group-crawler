from datetime import datetime
from dateutil.relativedelta import relativedelta
from crawler import Crawler
import asyncio

APP_NAME = 'Your app name'
API_ID = 'Your api ID'
API_HASH = 'Your api hash'
GROUPS_TO_CRAWL_FROM = ['group id (link or id as number)']

async def main():
    crawler = await Crawler.create(APP_NAME, API_ID, API_HASH, GROUPS_TO_CRAWL_FROM)
    await crawler.start(since_stamp=datetime.utcnow() - relativedelta(days=30))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
