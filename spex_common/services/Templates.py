from spex_common.modules.database import db_instance
from spex_common.models.Templates import template
from spex_common.services.Utils import first_or_none, map_or_none
from .Pipeline import select_pipeline, recursion_query


collection = "templates"


def select(id):
    search = "FILTER doc._key == @value LIMIT 1"
    items = db_instance().select(collection, search, value=id)
    return first_or_none(items, template)


def select_template(**kwargs):
    search = db_instance().get_search(**kwargs)
    items = db_instance().select(collection, search, **kwargs)
    return map_or_none(items, lambda item: template(item).to_json())


def update(id, data=None):
    search = "FILTER doc._key == @value LIMIT 1 "
    items = db_instance().update(collection, data, search, value=id)
    return first_or_none(items, template)


def delete(**kwargs):
    search = db_instance().get_search(**kwargs)
    items = db_instance().delete(collection, search, **kwargs)
    return first_or_none(items, template)


def insert(data):
    item = db_instance().insert(collection, data)
    return template(item["new"]) if item["new"] is not None else None


def count():
    arr = db_instance().count(collection, "")
    return arr[0]


def trim(values: list[dict]):
    if values:
        for val in values:
            new_arr = []
            for key in [key for key in list(val.keys()) if key not in ["name", "jobs"]]:
                val.pop(key, None)
            if jobs := val.get('jobs'):
                val["jobs"] = trim(jobs)

            new_arr.append(val)
    return new_arr


def get_template_tree(pipeline_id: str, **kwargs):
    _pipelines = select_pipeline(collection="pipeline", _key=pipeline_id, **kwargs)
    lines = []
    if _pipelines is None:
        return []
    for _pipeline in _pipelines:
        res: list = []
        jobs = select_pipeline(
            _from=_pipeline.get("_id"), pipeline=_pipeline.get("id"), **kwargs
        )
        if jobs is None:
            continue
        for job in jobs:
            append_jobs = recursion_query(job["_to"], {}, 0, pipeline_id)
            append_jobs = trim([append_jobs])
            res.append(append_jobs)
        template: dict = {}
        template.update({"jobs": res})
        lines.append(template)

        return lines
