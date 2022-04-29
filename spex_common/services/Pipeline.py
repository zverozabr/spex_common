from spex_common.modules.database import db_instance
from spex_common.models.Pipeline import pipeline
from spex_common.services.Utils import first_or_none, map_or_none
import spex_common.services.Task as TaskService


collectionName = 'pipeline_direction'


def select(id, collection=collectionName, to_json=False, one=False):
    search = 'FILTER doc._key == @value LIMIT 1'
    items = db_instance().select(collection, search, value=id)

    def transform(item):
        item = pipeline(item)
        return item.to_json() if to_json else item

    if one:
        return first_or_none(items, transform)

    return map_or_none(items, transform)


def select_pipeline(condition=None, collection=collectionName, one=False, **kwargs):
    search = db_instance().get_search(**kwargs)
    if condition is not None and search:
        search = search.replace('==',  condition)

    items = db_instance().select(collection, search, **kwargs)

    def to_json(_item):
        return pipeline(_item).to_json()

    return first_or_none(items, to_json) \
        if one \
        else map_or_none(items, to_json)


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
    query = f"""
        FOR doc IN jobs
        FILTER doc._id == @itemid
        RETURN {{
            id: doc._key, 
            name: doc.name, 
            status: doc.status,
            jobs: (
                FOR item IN pipeline_direction 
                FILTER item._from == @itemid 
                    && item.pipeline == @pipeline_id 
                RETURN {{
                    name: item.name, 
                    _id: SUBSTITUTE(item._to, "jobs/", ""), 
                    status: item.complete 
                }}
            )
        }}
        """

    result = db_instance().query(
        query,
        itemid=itemid,
        pipeline_id=pipeline_id
    )

    if not result:
        return tree

    tree = result[0]
    tree['tasks'] = TaskService.select_tasks_edge(itemid)

    if _depth < 50 and tree.get('jobs'):
        for index, job in enumerate(tree['jobs']):
            _id = f'jobs/{job["_id"]}'
            tree['jobs'][index] = recursion_query(
                _id,
                job,
                _depth + 1,
                pipeline_id
            )

    return tree


def depth(x):
    if type(x) is dict and x:
        return 1 + max(depth(x[a]) for a in x)
    if type(x) is list and x:
        return 1 + max(depth(a) for a in x)
    return 0


def get_jobs(x, prefix=True):
    jobs = []
    if not isinstance(x, list):
        return jobs

    for job in x:
        if job is None:
            continue
        if not prefix:
            jobs.append(job.get("_id", job.get("id")))
        else:
            jobs.append(f'jobs/{job.get("_id", job.get("id"))}')

        jobs = jobs + get_jobs(job.get('jobs'), prefix)

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
