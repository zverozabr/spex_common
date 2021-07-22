from os import getenv
from .model import Redis

__instance: Redis or None = None


def redis_instance() -> Redis:
    global __instance
    if __instance is None:
        __instance = Redis(
            getenv('REDIS_HOST'),
            int(getenv('REDIS_PORT', 6379)),
            getenv('REDIS_PASSWORD')
        )
        __instance.initialize()

    return __instance
