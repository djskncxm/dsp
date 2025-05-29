import asyncio
from asyncio import Semaphore, BoundedSemaphore

semaphore = BoundedSemaphore(5)


async def demo():
    semaphore.release()
    print(semaphore._value)


asyncio.run(demo())
