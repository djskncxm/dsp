import random
from dsp.middleware import BaseMiddleware


class TestMiddleware(BaseMiddleware):
    def process_request(self, request, spider):
        print("process_request =>", request, spider)

    def process_response(self, request, response, spider):
        print("process_response =>", request, response, spider)
        return response

    def process_exception(self, request, exc, spider):
        print("process_exception => ", request, exc, spider)


class TestMiddleware2(BaseMiddleware):
    def process_request(self, request, spider):
        if random.randint(1, 3) == 1:
            1 / 0
        # pass

    def process_exception(self, request, exc, spider):
        if isinstance(exc, ZeroDivisionError):
            print("已经处理")
            return True


class TestMiddleware3(BaseMiddleware):
    def process_response(self, request, response, spider):
        print("process_response3 =>", request, response, spider)
        return response
