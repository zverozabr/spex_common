from pickle import loads, dumps
import uuid


class RedisEvent:
    def __init__(self, type, data, id=None):
        self.type = type
        self.data = data
        self.id = id or uuid.uuid4()

    def serialize(self):
        result = dumps(self)
        return result

    @classmethod
    def deserialize(cls, buffer):
        event = loads(buffer)

        if not isinstance(event, cls):
            raise Exception('Not an event')

        return event

    def __repr__(self):
        return f'RedisEvent(type={self.type}, data={self.data}, id={self.id})'
