import time
import ujson
from arango import ArangoClient
from arango.database import StandardDatabase, AsyncDatabase
from arango.job import AsyncJob


def receive_async_response(task: AsyncJob):
    while task.status() != 'done':
        time.sleep(0.1)
    return [i for i in task.result()]


class ArangoDB:
    client: ArangoClient
    instance: StandardDatabase
    async_instance: AsyncDatabase

    def __init__(
        self,
        hosts: str = '0.0.0.0:8529',
        database: str = 'genentechdb',
        username: str = '',
        password: str = '',
    ):
        self.client = ArangoClient(
            hosts,
            serializer=ujson.dumps,
            deserializer=ujson.loads,
        )
        self.username = username
        self.password = password
        self.database = database

    def initialize(self):
        sys_db = self.client.db(
            '_system',
            username=self.username,
            password=self.password
        )

        if not sys_db.has_database(self.database):
            sys_db.create_database(self.database)

        self.instance = self.client.db(
            self.database,
            self.username,
            self.password
        )
        self.password = None
        self.async_instance = self.instance.begin_async_execution(return_result=True)

        db = self.instance

        if not db.has_collection('users'):
            collection = db.create_collection('users')
            collection.add_hash_index(fields=["username"], unique=True)
        if not db.has_collection('images'):
            db.create_collection('images')
        if not db.has_collection('groups'):
            db.create_collection('groups')
        if not db.has_collection('jobs'):
            db.create_collection('jobs')
        if not db.has_collection('tasks'):
            db.create_collection('tasks')
        if not db.has_collection('projects'):
            db.create_collection('projects')
        if not db.has_collection('jobs_tasks'):
            db.create_collection('jobs_tasks', edge=True)
        if not db.has_collection('resource'):
            db.create_collection('resource')
        if not db.has_collection('box'):
            db.create_collection('box')
        if not db.has_collection('pipeline'):
            db.create_collection('pipeline')
        if not db.has_collection('history'):
            db.create_collection('history')
        if not db.has_collection('templates'):
            db.create_collection('templates')
        if not db.has_collection('waiting_table'):
            db.create_collection('waiting_table')
        if not db.has_collection('pipeline_direction'):
            db.create_collection('pipeline_direction', edge=True)
        if not db.has_graph('pipeline'):
            pipeline = db.create_graph('pipeline')
            pipeline.create_edge_definition(edge_collection='pipeline_direction', from_vertex_collections=['box', 'pipeline', 'projects'], to_vertex_collections=['tasks', 'box', 'pipeline'])

    def insert(self, collection, data, overwrite_mode=None):
        return self.instance.insert_document(collection, data, True, overwrite_mode=overwrite_mode)

    def query(self, query, **kwargs):
        task = self.async_instance.aql.execute(
            query,
            bind_vars={
                **kwargs
            }
        )
        return receive_async_response(task)

    def select(self, collection, search='', fields='doc', **kwargs):
        return self.query(
            f'FOR doc IN {collection} {search} RETURN {fields}',
            **kwargs
        )

    def update(self, collection, data, search='', **kwargs):
        task = self.async_instance.aql.execute(
            f'FOR doc IN {collection}'
            f' {search}'
            f' UPDATE doc WITH {data} IN {collection}'
            f' LET updated = NEW'
            f' Return UNSET(updated, "_rev", "password")',
            bind_vars={
                **kwargs
            }
        )
        return receive_async_response(task)

    def delete(self, collection, search='', **kwargs):
        task = self.async_instance.aql.execute(
            f'FOR doc IN {collection}'
            f' {search}'
            f' REMOVE doc IN {collection} '
            f' LET deleted = OLD '
            f' RETURN UNSET(deleted, "_rev", "password") ',
            bind_vars={
                **kwargs
            }
        )
        return receive_async_response(task)

    def count(self, collection, search='', **kwargs):
        task = self.async_instance.aql.execute(
            f'FOR doc IN {collection}'
            f' {search}'
            f' COLLECT WITH COUNT INTO length'
            f' RETURN length',
            bind_vars={
                **kwargs
            }
        )
        return receive_async_response(task)

    def insert_edge(self, collection, _from='', _to=''):
        task = self.async_instance.aql.execute(
            f'INSERT {{ _from: @from, _to: @to }}'
            f' INTO {collection}',
            bind_vars={
                'from': _from,
                'to': _to,
            }
        )
        return receive_async_response(task)

    def select_edge(self, collection, inbound, _key):
        inbound = 'inbound' if inbound else 'outbound'

        task = self.async_instance.aql.execute(
            f'FOR doc IN {inbound} @key {collection}'
            f' RETURN doc',
            bind_vars={
                'key': _key,
            }
        )
        return receive_async_response(task)

    def get_search(self, **kwargs):
        keys = kwargs.keys()
        if len(keys) < 1:
            return ''

        args = [f'doc.{key} == @{key}' for key in keys]

        return f'FILTER {" && ".join(args)}'
