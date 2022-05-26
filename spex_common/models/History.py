class History:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_key', '')
        self.author = kwargs.get('author', '')
        self.date = kwargs.get('date', '')
        self.content = kwargs.get('content', '')
        self.parent = kwargs.get('parent', '')
        self.event_type = kwargs.get('event_type', '')

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'date': self.date,
            'content': self.content,
            'parent': self.parent,
            'event_type': self.event_type
        }


def history(data):
    return History(**data)
