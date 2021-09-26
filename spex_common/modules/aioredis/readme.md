# Asynchronous redis client

To subscribe to events from redis:
```python
from spex_common.modules.aioredis import create_aioredis_clien

redis_client = create_aioredis_client()

@redis_client.event('some_event')
async def listener(event):
    # event is RedisEvent
    print(event)

if __name__ == '__main__':
    redis_client.run()
```
In order to avoid listening blocking using `create_aioredis_client()`

But if we just want to send an event we can use `send_event` method:
```python
import uuid
from spex_common.config import load_config
from spex_common.modules.aioredis import send_event
from spex_common.services.Timer import every


def emitter():
    send_event('some_event', {
        'omero_img_id': 11,
        'override': True,
        'athing': uuid.uuid4()
    })


if __name__ == '__main__':
    load_config()
    every(20, emitter)
```
