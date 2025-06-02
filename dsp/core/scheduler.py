import asyncio
from typing import Optional

from dsp.utils.pqueue import SpiderPriorityQueue
from dsp.utils.log import get_logger


class Scheduler:
    def __init__(self, crawler):
        self.request_queue: Optional[SpiderPriorityQueue] = None
        self.crawler = crawler
        self.item_count = 0
        self.request_count = 0
        self.logger = get_logger(
            self.__class__.__name__, log_level=crawler.settings["LOG_LEVEL"]
        )

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_request(self):
        request = await self.request_queue.get()
        return request

    async def enqueue_request(self, request):
        await self.request_queue.put(request)
        self.crawler.stats.inc_value("request_Scheduler_count")

    def idle(self) -> bool:
        return len(self) == 0

    async def interval_log(self, interval):
        while True:
            last_item_count = self.crawler.stats.get_value(
                "item_successful_count", default=0
            )
            last_response_count = self.crawler.stats.get_value(
                "response_received_count", default=0
            )
            item_rate = last_item_count - self.item_count
            response_rate = last_response_count - self.request_count
            self.item_count, self.request_count = last_item_count, last_response_count
            self.logger.info(
                f"Crawled {last_response_count} page (at {response_rate} pages/{interval}s),"
                f"Got {last_item_count} page (at {item_rate} pages/{interval}s),"
            )
            await asyncio.sleep(interval)

    def __len__(self):
        return self.request_queue.qsize()
