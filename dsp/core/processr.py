from typing import Union
from asyncio import Queue

from dsp import Request, Item


class Processor:
    def __init__(self, crawler):
        self.crawler = crawler
        self.queue: Queue = Queue()

    async def process(self):
        while not self.idle():
            result = await self.queue.get()
            if isinstance(result, Request):
                await self.crawler.engine.enqueue_request(result)
            else:
                assert isinstance(result, Item)
                await self._proces_item(result)

    async def _proces_item(self, item):
        self.crawler.stats.inc_value("item_successful_count")
        print(item)

    async def enqueue(self, output: Union[Request, Item]):
        await self.queue.put(output)
        await self.process()

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()
