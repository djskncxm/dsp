from typing import Optional

import httpx

from dsp import Response
from dsp.utils.log import get_logger
from dsp.core.downloader import ActiveRequestManager


class HTTPXDownloader:
    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, crawler.settings["LOG_LEVEL"])
        self._clinet: Optional[httpx.AsyncClient] = None
        self._timeout: Optional[httpx.Timeout] = None

    def open(self):
        self.logger.info(
            f"{self.crawler.spider} => <downloader class => {type(self).__name__}> "
            f"<concurrency => {self.crawler.settings['CONCURRENCY']}> "
        )
        request_timeout = self.crawler.settings["REQUEST_TIMEOUT"]
        self._timeout = httpx.Timeout(timeout=request_timeout)

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request)
            return response

    async def download(self, request) -> Optional[Response]:
        try:
            proxies = request.proxy
            async with httpx.AsyncClient(
                timeout=self._timeout, proxies=proxies
            ) as clinet:
                self.logger.debug(
                    f"request downloader => {request.url}, method => {request.method}"
                )
                response = await clinet.request(
                    request.method,
                    url=request.url,
                    headers=request.headers,
                    cookies=request.cookies,
                    data=request.body,
                )
                body = await response.aread()
        except Exception as e:
            self.logger.error(f"Error during request: {e}")
            return None
        else:
            self.crawler.stats.inc_value("response_received_count")
        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body) -> Optional[Response]:
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status_code,
            body=body,
            request=request,
        )

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        pass
