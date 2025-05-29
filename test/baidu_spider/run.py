import asyncio
import time

from dsp.utils.project import get_settings
from dsp.crawler import CrawlerProcess
from test.baidu_spider.spider.baidu import BaiduSpider


async def run():
    settings = get_settings()
    process = CrawlerProcess(settings)
    await process.crawl(BaiduSpider)
    # await process.crawl(BaiduSpider2)
    await process.start()


s = time.time()
asyncio.run(run())
print(time.time() - s)
