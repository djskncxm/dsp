from inspect import isgenerator, isasyncgen

from dsp.exceptions import TransfromTypeError


async def transform(func_result):
    if isgenerator(func_result):
        for r in func_result:
            yield r
    elif isasyncgen(func_result):
        async for r in func_result:
            yield r
    else:
        raise TransfromTypeError(
            "回调函数的返回值必须是一个generator或者是异步的generator"
        )
