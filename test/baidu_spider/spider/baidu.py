from dsp import Request
from dsp.spider import Spider


class BaiduSpider(Spider):
    def __init__(self):
        self.start_urls = ["https://www.baidu.com/", "https://www.baidu.com"]

    def parse(self, response):
        print("response => ", response)
        for i in range(10):
            url = "https://www.baidu.com/"
            request = Request(url=url, callback=self.parse_page)
            yield request

    def parse_page(self, response):
        print("parse_page response => ", response)
        for i in range(10):
            url = "https://www.baidu.com/"
            request = Request(url=url, callback=self.parse_detail)
            yield request

    def parse_detail(self, response):
        print("parse_detail response => ", response)
