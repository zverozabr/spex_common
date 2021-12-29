import asyncio
from aioredis import Redis
from ...models.RedisEvent import RedisEvent


loop = asyncio.get_event_loop()


class AIORedisClient:
    _events = {}

    def __init__(self, host="localhost", port=6379, password=None, db=0, **kwargs):
        kwargs.update({
            'host': host,
            'port': port,
            'password': password,
            'db': db
        })
        loop.run_until_complete(self.__async_init(**kwargs))

    async def __async_init(self, **kwargs):
        self.sender = await Redis(**kwargs)
        self.receiver = await Redis(**kwargs)

    async def __send(self, key, event: RedisEvent):
        await self.sender.rpush(key, event.serialize())

    async def __receive(self, *keys, timeout=0):
        key, raw_msg = await self.receiver.blpop(*keys, timeout=timeout)
        return RedisEvent.deserialize(raw_msg)

    async def wait_for_event(self, timeout=0):
        return await self.__receive(*self._events.keys(), timeout=timeout)

    async def dispatch_event(self, event: RedisEvent):
        if event.type in self._events:
            for handler in self._events[event.type]:
                loop.create_task(handler(event))

    async def send(self, event: RedisEvent):
        await self.__send(event.type, event)

    async def wait_for_reply(self, to: RedisEvent, *, timeout=0):
        return await self.__receive(to.id, timeout=timeout)

    async def send_reply(self, to: RedisEvent, reply: RedisEvent):
        await self.__send(to.id, reply)

    def event(self, type: str):
        if type not in self._events:
            self._events[type] = []

        def register(handler):
            if asyncio.iscoroutine(handler):
                raise ValueError('Handler must be a coroutine.')
            self._events[type].append(handler)

        return register

    # Run this to wait for and dispatch events
    async def listen_for_events(self):
        while 1:
            event = await self.wait_for_event()
            await self.dispatch_event(event)

    def run(self):
        loop.run_until_complete(self.listen_for_events())

    async def __close__(self):
        await self.receiver.close()
        await self.sender.close()

    def close(self):
        loop.run_until_complete(self.__close__())
