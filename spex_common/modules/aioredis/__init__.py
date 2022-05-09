import asyncio
from os import getenv
from ...models.RedisEvent import RedisEvent
from .model import AIORedisClient


__instance: AIORedisClient or None = None


def create_aioredis_client(**kwargs) -> AIORedisClient:
    return AIORedisClient(
        getenv('REDIS_HOST'),
        int(getenv('REDIS_PORT', 6379)),
        getenv('REDIS_PASSWORD'),
        max_connections=8,
        **kwargs
    )


def aioredis_sender_instance() -> AIORedisClient:
    global __instance
    if __instance is None:
        __instance = create_aioredis_client()

    return __instance


def send_event(event_type: str, data, **kwargs):
    client = aioredis_sender_instance()

    event = RedisEvent(event_type, data, **kwargs)

    loop = asyncio.get_event_loop()

    if loop.is_running():
        loop.create_task(client.send(event))
        return

    loop.run_until_complete(client.send(event))
