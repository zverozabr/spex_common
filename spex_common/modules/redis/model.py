import redis
import json


class Redis:
    client: redis.Redis = None
    redis_pass: str = ''

    def __init__(
        self,
        hosts: str = '0.0.0.0',
        port: int = 6379,
        redis_pass: str = ''
    ):
        self.client = redis.Redis(hosts, port, db=0, password=redis_pass)
        self.redis_pass = redis_pass

    def initialize(self):
        self.client.execute_command('PING 123')

    def insert(self, collection, data):
        return self.client.execute_command('JSON.SET', collection + '/' + list(data.keys())[0], '.', json.dumps(data))

    def select(self, collection, **kwargs):
        item = self.client.execute_command('JSON.GET', collection, **kwargs)
        if item is not None:
            return json.loads(item)
        else:
            return None

    def remove(self, collection):
        return self.client.execute_command('JSON.DEL', collection)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, **kwargs):
        return self.client.set(key, value, **kwargs)

    def delete(self, *keys):
        return self.client.delete(*keys)

    def keys(self, pattern='*'):
        return self.client.keys(pattern)

    def count(self, search='*'):
        return len(self.keys(search))
