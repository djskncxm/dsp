import asyncio
from inspect import iscoroutine
from operator import setitem
from typing import Optional, Generator, Callable

from dsp import Request
from dsp.core.downloader import Downloader
from dsp.core.scheduler import Scheduler
from dsp.spider import Spider
from dsp.utils.spider import transform
from dsp.exceptions import OutputError
from dsp.task_manager import TaskManager


class Engine:
    def __init__(self, settings):
        self.downloader: Optional[Downloader] = None
        self.start_requests: Optional[Generator] = None
        self.scheduler: Optional[Scheduler] = None
        self.spider: Optional[Spider] = None
        self.task_manager: TaskManager = TaskManager(settings.getint("CONCURRENCY"))
        self.running = False

    async def start_spider(self, spider: Spider):
        self.running = True
        self.spider = spider
        self.downloader = Downloader()
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, "open"):
            self.scheduler.open()
        self.start_requests = iter(spider.start_requests())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
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
                else:
                    await self.enqueue_request(start_request)

    async def _fetch(self, request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            if _outputs := callback(_response):
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    return transform(_outputs)

        _response = await self.downloader.fetch(request)
        output = await _success(_response)
        return output

    async def _crawl(self, request):
        async def crawl_task():
            outputs = await self._fetch(request)
            if outputs:
                await self._handle_spider_output(outputs)

        # asyncio.create_task(crawl_task())
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
            if isinstance(output, Request):
                await self.enqueue_request(output)
            else:
                raise OutputError(f"{type(self.spider)}")

    async def _exit(self):
        if (
            self.scheduler.idle()
            and self.downloader.idle()
            and self.task_manager.all_done()
        ):
            return True
        return False
