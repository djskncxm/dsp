import asyncio
from inspect import iscoroutine
from typing import Optional, Generator, Callable

from dsp import Request, Item
from dsp.core.scheduler import Scheduler
from dsp.spider import Spider
from dsp.utils.spider import transform
from dsp.exceptions import OutputError
from dsp.task_manager import TaskManager
from dsp.core.processr import Processor
from dsp.utils.log import get_logger
from dsp.utils.project import load_class
from dsp.core.downloader import DownloaderBase


class Engine:
    def __init__(self, crawler):
        self.logger = get_logger(
            self.__class__.__name__, log_level=crawler.settings["LOG_LEVEL"]
        )
        self.processor = None
        self.crawler = crawler
        self.downloader: Optional[DownloaderBase] = None
        self.start_requests: Optional[Generator] = None
        self.scheduler: Optional[Scheduler] = None
        self.spider: Optional[Spider] = None
        self.settings = crawler.settings
        self.task_manager: TaskManager = TaskManager(
            self.settings.getint("CONCURRENCY")
        )
        self.running = False
        self.normal = True

    def _get_downloader_cls(self):
        downloader_cls = load_class(self.settings["DOWNLOAD"])
        if not issubclass(downloader_cls, DownloaderBase):
            raise TypeError(
                f"The downloader class ({self.settings['DOWNLOAD']}) dosen't fully implemented require interface"
            )
        return downloader_cls

    async def start_spider(self, spider: Spider):
        self.running = True
        self.logger.info(f"dsp started. (project name:{self.settings['PROJECT_NAME']})")
        self.logger.debug(f"dsp started. (project name:{self.settings['LOG_LEVEL']})")
        self.spider = spider
        downloader_cls = self._get_downloader_cls()
        self.downloader = downloader_cls.create_instance(self.crawler)
        if hasattr(self.downloader, "open"):
            self.downloader.open()
        self.scheduler = Scheduler(self.crawler)
        self.processor = Processor(self.crawler)
        if hasattr(self.scheduler, "open"):
            self.scheduler.open()
        self.start_requests = iter(spider.start_requests())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        asyncio.create_task(self.scheduler.interval_log(self.settings["INTERVAL"]))
        await crawling

    async def crawl(self):
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    start_request = next(self.start_requests)
                except StopIteration:
                    self.start_requests = None
                except Exception as e:
                    if not await self._exit():
                        continue
                    self.running = False
                    if self.start_requests is not None:
                        self.logger.error(f"Error during start_requests => {e}")
                else:
                    await self.enqueue_request(start_request)
        if not self.running:
            await self.close_spider()

    async def _fetch(self, request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            if _outputs := callback(_response):
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    return transform(_outputs)

        _response = await self.downloader.fetch(request)
        if _response is None:
            return None
        output = await _success(_response)
        return output

    async def _crawl(self, request):
        async def crawl_task():
            outputs = await self._fetch(request)
            if outputs:
                await self._handle_spider_output(outputs)

        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

    async def enqueue_request(self, request):
        await self._schedule_request(request)

    async def _schedule_request(self, request):
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        return await self.scheduler.next_request()

    async def _handle_spider_output(self, outputs):
        async for output in outputs:
            if isinstance(output, (Request, Item)):
                await self.processor.enqueue(output)
            else:
                raise OutputError(f"{type(self.spider)}")

    async def _exit(self):
        if (
            self.scheduler.idle()
            and self.downloader.idle()
            and self.task_manager.all_done()
            and self.processor.idle()
        ):
            return True
        return False

    async def close_spider(self):
        await asyncio.gather(*self.task_manager.current_task)
        await self.downloader.close()
        if self.normal:
            await self.crawler.close()
