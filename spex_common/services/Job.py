from spex_common.modules.database import db_instance
from spex_common.models.Job import job, Job
from spex_common.models.Connection import connection
from spex_common.services.Utils import first_or_none, map_or_none
import spex_common.services.Task as TaskService


collection = 'jobs'


def select(id, collection='jobs') -> Job or None:
    value = id
    search = 'FILTER doc._key == @value LIMIT 1'
    items = db_instance().select(collection, search, value=value)
    return first_or_none(items, job)


def select_jobs(collection='jobs', condition=None, **kwargs) -> list[Job] or None:
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)

    items = db_instance().select(collection, search, **kwargs)
    return map_or_none(items, lambda item: job(item).to_json())


def update(id, collection='jobs', data=None) -> Job or None:
    search = 'FILTER doc._key == @value LIMIT 1 '
    items = db_instance().update(collection, data, search, value=id)
    return first_or_none(items, job)


def delete(id, collection='jobs') -> Job or None:
    search = 'FILTER doc._key == @value LIMIT 1 '
    items = db_instance().delete(collection, search, value=id)
    return first_or_none(items, job)


def delete_connection(condition=None, collection='jobs_tasks', **kwargs) -> Job or None:
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)
    items = db_instance().delete(collection, search, **kwargs)
    return first_or_none(items, job)


def select_connections(condition=None, collection="jobs_tasks", one=False, **kwargs):
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)

    items = db_instance().select(collection, search, **kwargs)

    def to_json(item):
        connection(item).to_json()

    if one:
        return first_or_none(items, to_json)

    return map_or_none(items, to_json)


def insert(data, collection='jobs') -> Job or None:
    item = db_instance().insert(collection, data)
    return first_or_none([item['new']], job)


def count(collection='jobs') -> int:
    arr = db_instance().count(collection, '')
    return arr[0]


def update_job(id, data):
    _job = update(id=id, data=data)

    if _job is None:
        return None

    _job = _job.to_json()

    tasks = TaskService.select_tasks_edge(_job['_id'])

    updated_tasks = []

    for item in tasks:
        item = TaskService.update(item.id, data)
        updated_tasks.append(item.to_json())
    _job['tasks'] = updated_tasks

    if _job.get('status') is None or _job.get('status') == '':
        _job.update(status=0)

    return _job
