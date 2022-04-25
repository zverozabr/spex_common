class Template:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_key', '')
        self.author = kwargs.get('author', '')
        self.data = kwargs.get('data', '')
        self.pipeline_source = kwargs.get('pipeline_source', '')
        self.name = kwargs.get('name', '')

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'data': self.data,
            'pipeline_source': self.pipeline_source,
            'name': self.name,
        }


def template(data):
    return Template(**data)
