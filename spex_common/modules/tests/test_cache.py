import unittest
from ..cache import cache_instance


class ClassInstance:
    def __init__(self, value):
        self.value = value


class CacheServiceTestCase(unittest.TestCase):
    def tearDown(self):
        cache_instance().delete('test1')
        cache_instance().delete('test2')

    def test_set_get(self):
        cache_instance().set('test1', 'a')
        value = cache_instance().get('test1')
        self.assertIsNotNone(value)
        self.assertEqual(value, 'a')

    def test_set_get_instance(self):
        item = ClassInstance(5)
        cache_instance().set('test2', item)
        item = cache_instance().get('test2')
        self.assertIsNotNone(item)
        self.assertIsInstance(item, ClassInstance)
        self.assertIsNotNone(item.value)
        self.assertEqual(item.value, 5)


if __name__ == '__main__':
    unittest.main()
