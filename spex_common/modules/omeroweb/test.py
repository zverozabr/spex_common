# noinspection PyUnresolvedReferences
import os
# import config
import unittest
from ...models import OmeroSession
from ..cache import cache_instance
from . import create
os.environ['MODE'] = 'test'


class OmeroWebTest(unittest.TestCase):

    def setUp(self):
        cache_instance().flush_all()

    def test_create_and_get(self):
        session = create('root', 'omero')

        self.assertIsNotNone(session)
        self.assertIsInstance(session, OmeroSession)


if __name__ == '__main__':
    unittest.main()
