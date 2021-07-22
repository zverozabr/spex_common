from os import getenv
from pymemcache.client.base import PooledClient
from pymemcache import serde

__instance: PooledClient or None = None


def cache_instance() -> PooledClient:
    global __instance
    if __instance is None:
        __instance = PooledClient(
            getenv('MEMCACHED_HOST', 'localhost:11211'),
            max_pool_size=8,
            serde=serde.pickle_serde
        )

    return __instance
