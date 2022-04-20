from pickle import loads, dumps


class Serializable:
    """
    This class is used to serialize and deserialize objects.
    """
    def serialize(self):
        return dumps(self)

    @classmethod
    def deserialize(cls, data):
        if not data:
            return None

        instance = loads(data)
        return instance if isinstance(instance, cls) else None
