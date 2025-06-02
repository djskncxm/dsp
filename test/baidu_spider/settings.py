PROJECT_NAME = "baidu_spider"

CONCURRENCY = 4
LOG_LEVEL = "DEBUG"

VERIFY_SSL = True

REQUEST_TIMEOUT = 5
# USE_SESSION = False
STATS_DUMP = True

DOWNLOAD = "dsp.core.downloader.aiohttp_downloader.AioDownloader"

MIDDLEWARES = [
    "baidu_spider.middleware.TestMiddleware",
    "baidu_spider.middleware.TestMiddleware2",
    "baidu_spider.middleware.TestMiddleware3",
]
