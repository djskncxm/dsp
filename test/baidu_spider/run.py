import asyncio
import time

from dsp.core.engine import Engine
from dsp.utils.project import get_settings
from dsp.settings.settings_manager import SettingManager
from baidu import BaiduSpider

async def run():
    settings = get_settings()
    print(settings)
    baidu = BaiduSpider()
    engine = Engine(settings)
    await  engine.start_spider(baidu)

s = time.time()
asyncio.run(run())
print(time.time() - s)