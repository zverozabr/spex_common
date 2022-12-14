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

        if loop.is_running():
            loop.create_task(self.__async_init(**kwargs))
            return

        loop.run_until_complete(self.__async_init(**kwargs))

    async def __async_init(self, **kwargs):
        self.sender = await Redis(**kwargs)
        self.receiver = await Redis(**kwargs)

    async def __send(self, key, event: RedisEvent):
        await self.sender.rpush(key, event.serialize())

    async def __set(self, key, value, **kwargs):
        return await self.sender.set(key, value, **kwargs)

    async def __get(self, key):
        return await self.receiver.get(key)

    async def __delete(self, *keys):
        return await self.receiver.delete(*keys)

    async def __keys(self):
        return await self.receiver.keys()

    async def __receive(self, *keys, timeout=0):
        data = await self.receiver.blpop(keys, timeout=timeout)
        if data is None:
            return None

        key, raw_msg = data

        return None if raw_msg is None else RedisEvent.deserialize(raw_msg)

    async def wait_for_event(self, timeout=0):
        return await self.__receive(*self._events.keys(), timeout=timeout)

    async def dispatch_event(self, event: RedisEvent):
        if event.type in self._events:
            for handler in self._events[event.type]:
                loop.create_task(handler(event))

    async def send(self, event: str or RedisEvent, data, **kwargs):
        if not isinstance(event, RedisEvent):
            event = RedisEvent(event, data, **kwargs)

        await self.__send(event.type, event)

    async def wait_for_reply(self, to: RedisEvent, *, timeout=0):
        return await self.__receive(to.id, timeout=timeout)

    async def send_reply(self, to: RedisEvent, reply: RedisEvent):
        await self.__send(to.id, reply)

    def event(self, event_type: str):
        if type not in self._events:
            self._events[event_type] = []

        def register(handler):
            if asyncio.iscoroutine(handler):
                raise ValueError('Handler must be a coroutine.')
            self._events[event_type].append(handler)

        return register

    # Run this to wait for and dispatch events
    async def listen_for_events(self, timeout=0):
        while 1:
            event = await self.wait_for_event(timeout)
            if event is not None:
                await self.dispatch_event(event)

    def run(self, timeout=0):
        loop.run_until_complete(self.listen_for_events(timeout))

    async def __close__(self):
        await self.receiver.close()
        await self.sender.close()

    def close(self):
        loop.run_until_complete(self.__close__())

    def set(self, key, value, **kwargs):
        return loop.run_until_complete(self.__set(key, value, **kwargs))

    def get(self, key):
        return loop.run_until_complete(self.__get(key))

    def delete(self, *keys):
        return loop.run_until_complete(self.__delete(*keys))

    def keys(self):
        return loop.run_until_complete(self.__keys())
