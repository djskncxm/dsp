import ujson
import re
from typing import Dict
from urllib.parse import urljoin as _urljoin

from parsel import Selector

from dsp import Request
from dsp.exceptions import DecodeError


class Response:
    def __init__(
        self,
        url: str,
        *,
        headers: Dict,
        body: bytes = b"",
        request: Request,
        status: int = 200,
    ):
        self.url = url
        self.headers = headers
        self.body = body
        self.request = request
        self.status = status
        self.encoding = request.encoding
        self._text_cache = None
        self._selector = None

    @property
    def text(self):
        if self._text_cache:
            return self._text_cache
        try:
            self._text_cache = self.body.decode(self.encoding)
        except UnicodeDecodeError:
            try:
                _encoding_re = re.compile("charset=([\w]+)", flags=re.I)
                _encoding_string = self.headers.get(
                    "Content-Type", ""
                ) or self.headers.get("content-type")
                _encoding = _encoding_re.search(_encoding_string)
                if _encoding:
                    _encoding = _encoding.group(1)
                    text = self.body.decode(self.encoding)
                else:
                    raise DecodeError(f"{self.request} {self.request.encoding}错误,")
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    e.encoding, e.object, e.start, e.end, f"{self.request}"
                )
        return self._text_cache

    def xpath(self, xpath_string):
        if self._selector is None:
            self._selector = Selector(self.text)
        return self._selector.xpath(xpath_string)

    def json(self):
        return ujson.load(self.text)

    def urljoin(self, url):
        return _urljoin(self.url, url)

    def __str__(self):
        return f"<{self.status}>"

    @property
    def meat(self):
        return self.request.meat
