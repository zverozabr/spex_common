class WaitTableEntry:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_key', '')
        self.author = kwargs.get('author', '')
        self.date = kwargs.get('date', '')
        self.who_waits = kwargs.get('who_waits', '')
        self.what_awaits = kwargs.get('what_awaits', '')

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'date': self.date,
            'who_waits': self.who_waits,
            'what_awaits': self.what_awaits,
        }


def wait_table_entry(data):
    return WaitTableEntry(**data)
