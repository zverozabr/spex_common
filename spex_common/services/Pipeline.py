from spex_common.modules.database import db_instance
from spex_common.models.Pipeline import pipeline
from spex_common.services.Utils import first_or_none, map_or_none
import spex_common.services.Task as TaskService


collectionName = 'pipeline_direction'


def select(id, collection=collectionName, to_json=False, one=False):
    search = 'FILTER doc._key == @value LIMIT 1'
    items = db_instance().select(collection, search, value=id)

    def to_json(item):
        return pipeline(item).to_json()

    if one:
        return first_or_none(items, to_json)
    return map_or_none(items, lambda item: (pipeline(item).to_json() if to_json else pipeline(item)))


def select_pipeline(condition=None, collection=collectionName, one=False, **kwargs):
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)

    items = db_instance().select(collection, search, **kwargs)

    def to_json(_item):
        return pipeline(_item).to_json()

    if one:
        item = first_or_none(items, pipeline)
        if item is not None:
            item = item.to_json()
        return item

    return map_or_none(items, to_json)


def select_pipeline_edge(_key):
    items = db_instance().select_edge(collection=collectionName, inboud=False, _key=_key)

    def to_json(item):
        return pipeline(item).to_json()

    if len(items) == 1:
        return first_or_none(items, to_json)

    return map_or_none(items, to_json)


def update(id, data=None, collection=collectionName):
    search = 'FILTER doc._key == @value LIMIT 1 '
    items = db_instance().update(collection, data, search, value=id)
    return first_or_none(items, pipeline)


def delete(condition=None, collection=collectionName, **kwargs):
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)
    items = db_instance().delete(collection, search, **kwargs)
    return first_or_none(items, pipeline)


def insert(data, collection=collectionName):
    item = db_instance().insert(collection, data)
    return pipeline(item['new']) if item['new'] is not None else None


def count():
    arr = db_instance().count(collectionName, '')
    return arr[0]


def recursion_query(itemid, tree, _depth, pipeline_id):

    text = 'FOR d IN jobs ' + \
           f'FILTER d._id == "{itemid}" ' + \
           'LET jobs = (' + \
           f'FOR b IN pipeline_direction FILTER b._from ==  "{itemid}" && b.pipeline == "{pipeline_id}" RETURN  ' + '{"name": b.name, "_id": SUBSTITUTE(b._to, "jobs/",""), "status": b.complete } )' + \
           ' RETURN MERGE({"id": d._key, "name": d.name, "status": d.status}, {"jobs": jobs})'

    result = db_instance().query(text)
    if len(result) > 0:
        tree = result[0]
        tree['tasks'] = TaskService.select_tasks_edge(itemid)
    else:
        return tree

    i = 0
    if _depth < 50:
        if result[0]['jobs'] is not None and len(result[0]['jobs']) > 0:
            while i < len(result[0]['jobs']):
                _id = 'jobs/' + result[0]['jobs'][i]['_id']
                tree['jobs'][i] = recursion_query(_id, tree['jobs'][i], _depth + 1, pipeline_id)
                i += 1
    return tree


def depth(x):
    if type(x) is dict and x:
        return 1 + max(depth(x[a]) for a in x)
    if type(x) is list and x:
        return 1 + max(depth(a) for a in x)
    return 0


def get_jobs(x):
    jobs = []
    if type(x) is list and x:
        for job in x:
            if job is None:
                return jobs
            jobs.append('jobs/'+job.get('id'))
            if job.get('jobs') is not None:
                jobs = jobs + get_jobs(job.get('jobs'))
    return jobs


def search_in_arr_dict(key, value, arr):
    founded = []
    for item in arr:
        item_value = item.get(key)
        if value is not None and item_value == value:
            founded.append(arr.index(item))
    return founded


def get_tree(pipeline_id: str, **kwargs):
    _pipelines = select_pipeline(collection='pipeline', _key=pipeline_id, **kwargs)
    lines = []
    if _pipelines is None:
        return []
    for _pipeline in _pipelines:
        res = []
        jobs = select_pipeline(_from=_pipeline.get('_id'), pipeline=_pipeline.get('id'), **kwargs)
        if jobs is None:
            _pipeline.pop('_from', None)
            _pipeline.pop('_to', None)
            _pipeline.update({'jobs': res})
            lines.append(_pipeline)
            continue
        for job in jobs:
            res.append(recursion_query(job['_to'], {}, 0, pipeline_id))
        _pipeline.pop('_from', None)
        _pipeline.pop('_to', None)
        _pipeline.update({'jobs': res})
        lines.append(_pipeline)

    return lines
