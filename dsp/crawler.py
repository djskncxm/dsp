import asyncio
import signal
from typing import Type, Final, Set, Optional

from dsp.settings.settings_manager import SettingManager
from dsp.core.engine import Engine
from dsp.exceptions import SpiderTypeError
from dsp.utils.project import merge_settings
from dsp.spider import Spider
from dsp.utils.log import get_logger
from dsp.stats_collector import StatsCollector
from dsp.utils.date import now

logger = get_logger(__name__)


class Crawler:
    def __init__(self, spider_cls, settings):
        self.spider_cls = spider_cls
        self.spider: Optional[Spider] = None
        self.engine: Optional[Engine] = None
        self.settings: SettingManager = settings.copy()
        self.stats: Optional[StatsCollector] = None

    async def crawl(self):
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        self.stats = self._create_stats()
        await self.engine.start_spider(self.spider)

    def _create_stats(self):
        stats = StatsCollector(self)
        stats["start_time"] = now()
        return stats

    def _create_engine(self):
        engine = Engine(self)
        return engine

    def _create_spider(self):
        spider = self.spider_cls.create_instance(self)
        self._set_spider(spider)
        return spider

    def _set_spider(self, spider):
        merge_settings(spider, self.settings)

    async def close(
        self,
        reason="finished",
    ):
        self.stats.close_spider(self.spider, reason)


class CrawlerProcess:
    def __init__(self, settings=None):
        self.crawlers: Final[Set] = set()
        self._active: Final[Set] = set()
        self.settings = settings
        signal.signal(signal.SIGINT, self._shutdown)

    async def start(self):
        await asyncio.gather(*self._active)

    async def crawl(self, spider: Type[Spider]):
        crawler: Crawler = self._create_crawl(spider)
        self.crawlers.add(crawler)
        task = await self._crawl(crawler)
        self._active.add(task)

    @staticmethod
    async def _crawl(crawler):
        return asyncio.create_task(crawler.crawl())

    def _create_crawl(self, spider_cls) -> Crawler:
        if isinstance(spider_cls, str):
            raise SpiderTypeError(f"{type(self)}.crawl args: String is not supported")
        crawler = Crawler(spider_cls, self.settings)
        return crawler

    def _shutdown(self, _signum, _frame):
        for crawler in self.crawlers:
            crawler.engine.running = False
            crawler.engine.normal = False
            crawler.stats.close_spider(crawler.spider, "<c-c>")
        logger.warning("spiders received c-c signal closed")
