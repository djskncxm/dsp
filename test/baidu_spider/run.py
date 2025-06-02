import asyncio

from dsp.utils.project import get_settings
from dsp.crawler import CrawlerProcess
from test.baidu_spider.spider.baidu import BaiduSpider
# from dsp.utils import system as _ Windows使用aiohttp添加代理


async def run():
    settings = get_settings()
    process = CrawlerProcess(settings)
    await process.crawl(BaiduSpider)
    await process.start()


asyncio.run(run())
