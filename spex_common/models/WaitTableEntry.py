class WaitTableEntry:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_key', '')
        self.author = kwargs.get('author', '')
        self.date = kwargs.get('date', '')
        self.waiter_id = kwargs.get('waiter_id', '')
        self.waiter_type = kwargs.get('waiter_type', '')
        self.what_awaits = kwargs.get('what_awaits', '')

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'date': self.date,
            'waiter_id': self.waiter_id,
            'waiter_type': self.waiter_type,
            'what_awaits': self.what_awaits,
        }


def wait_table_entry(data):
    return WaitTableEntry(**data)
