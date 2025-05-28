import asyncio
import time

from dsp.core.engine import Engine
from baidu import BaiduSpider

async def run():
    baidu = BaiduSpider()
    engine = Engine()
    await  engine.start_spider(baidu)

s = time.time()
asyncio.run(run())
print(time.time() - s)