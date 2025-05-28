import requests
import asyncio

from dsp import Request

class Downloader:
    def __init__(self):
        self._active = set()
    async def fetch(self,request):
        self._active.add(request)
        response =  await self.download(request)
        self._active.remove(request)
        return response

    async def download(self,request:Request):
        response = requests.get(url=request.url)
        print("--------------------")
        return response

    def idle(self) -> bool:
        return len(self) == 0
    def __len__(self):
        return len(self._active)
