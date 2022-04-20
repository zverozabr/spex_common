from spex_common.modules.database import db_instance
from spex_common.models.Templates import template
from spex_common.services.Utils import first_or_none, map_or_none


collection = 'templates'

def select(id):
    search = 'FILTER doc._key == @value LIMIT 1'
    items = db_instance().select(collection, search, value=id)
    return first_or_none(items, template)


def select_template(**kwargs):
    search = db_instance().get_search(**kwargs)
    items = db_instance().select(collection, search, **kwargs)
    return map_or_none(items, lambda item: template(item).to_json())


def update(id, data=None):
    search = 'FILTER doc._key == @value LIMIT 1 '
    items = db_instance().update(collection, data, search, value=id)
    return first_or_none(items, template)


def delete(**kwargs):
    search = db_instance().get_search(**kwargs)
    items = db_instance().delete(collection, search, **kwargs)
    return first_or_none(items, template)


def insert(data):
    item = db_instance().insert(collection, data)
    return template(item['new']) if item['new'] is not None else None


def count():
    arr = db_instance().count(collection, '')
    return arr[0]
