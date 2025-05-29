from dsp import Request


class Spider:
    def __init__(self):
        if not hasattr(self, "start_url"):
            self.start_urls = []
        self.crawler = None

    def start_requests(self):
        if self.start_urls:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            if hasattr(self, "start_url") and isinstance(
                getattr(self, "start_url"), str
            ):
                yield Request(getattr(self, "start_url"))

    def parse(self, response):
        raise NotImplementedError

    @classmethod
    def create_instance(cls, crawler):
        o = cls()
        o.crawler = crawler
        return o

    def __str__(self):
        return self.__class__.__name__
