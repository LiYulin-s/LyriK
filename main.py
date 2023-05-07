from dbus_next.aio import MessageBus

import asyncio

async def func_a():
    await asyncio.sleep(2)
    print(65)

async def func_b():
    await asyncio.sleep(5)
    print(56)

loop = asyncio.get_event_loop()
