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

    def get_keys(self, search, **kwargs):
        keys = self.client.execute_command('keys ' + search, **kwargs)
        return keys

    def update(self, collection, data, search='', **kwargs):
        print('update')

    def delete(self, collection, search='', **kwargs):
        return self.client.execute_command('JSON.DEL', collection)

    def count(self, search='*', **kwargs):
        return self.client.execute_command('KEYS', search)
