import unittest
from ideal_completion import filter_items

class TestFilterItems(unittest.TestCase):
    def test_filter_items_age_greater_than_30(self):
        # Test filtering items where age is greater than 30
        collection_of_stuff = [
            {'name': 'Anna', 'age': 28},
            {'name': 'Dave', 'age': 32},
            {'name': 'Ella', 'age': 40}
        ]
        result = filter_items(collection_of_stuff, 'age', lambda v: v > 30)
        expected = [
            {'name': 'Dave', 'age': 32},
            {'name': 'Ella', 'age': 40}
        ]
        self.assertEqual(result, expected)

    def test_filter_items_name_starts_with_E(self):
        # Test filtering items where name starts with 'E'
        collection_of_stuff = [
            {'name': 'Anna', 'age': 28},
            {'name': 'Eve', 'age': 25},
            {'name': 'Ella', 'age': 40}
        ]
        result = filter_items(collection_of_stuff, 'name', lambda v: v.startswith('E'))
        expected = [
            {'name': 'Eve', 'age': 25},
            {'name': 'Ella', 'age': 40}
        ]
        self.assertEqual(result, expected)

    def test_filter_items_no_matching_condition(self):
        # Test filtering items where condition does not match any item
        collection_of_stuff = [
            {'name': 'Anna', 'age': 28},
            {'name': 'Dave', 'age': 32}
        ]
        result = filter_items(collection_of_stuff, 'age', lambda v: v > 50)
        expected = []
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()