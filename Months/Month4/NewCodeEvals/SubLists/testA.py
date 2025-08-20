import unittest
import pandas as pd
from ideal_completion import items_to_distributed_sublists

class TestItemsToDistributedSublists(unittest.TestCase):
    def test_items_more_than_collections(self):
        # Test when there are more items than collections
        items = pd.Series([10, 20, 30, 40, 50])
        num_collections = 3
        collections = items_to_distributed_sublists(items, num_collections)
        self.assertEqual(len(collections), num_collections)
        total_items = sum(len(collection) for collection in collections)
        self.assertEqual(total_items, len(items))
        for collection in collections:
            self.assertGreater(len(collection), 0)

    def test_items_less_than_collections(self):
        # Test when there are fewer items than collections
        items = pd.Series([5, 15])
        num_collections = 5
        collections = items_to_distributed_sublists(items, num_collections)
        self.assertEqual(len(collections), num_collections)
        total_items = sum(len(collection) for collection in collections)
        self.assertEqual(total_items, len(items))
        # Ensure that no collection is empty
        non_empty_collections = [collection for collection in collections if len(collection) > 0]
        self.assertEqual(len(non_empty_collections), len(items))

    def test_items_equal_collections(self):
        # Test when the number of items equals the number of collections
        items = pd.Series([2, 4, 6, 8])
        num_collections = 4
        collections = items_to_distributed_sublists(items, num_collections)
        self.assertEqual(len(collections), num_collections)
        total_items = sum(len(collection) for collection in collections)
        self.assertEqual(total_items, len(items))
        # Ensure each collection has exactly one item
        for collection in collections:
            self.assertEqual(len(collection), 1)

    def test_empty_items(self):
        # Test when items_to_distribute is empty
        items = pd.Series([], dtype=float)
        num_collections = 3
        collections = items_to_distributed_sublists(items, num_collections)
        self.assertEqual(len(collections), num_collections)
        total_items = sum(len(collection) for collection in collections)
        self.assertEqual(total_items, 0)
        for collection in collections:
            self.assertEqual(len(collection), 0)

    def test_zero_collections(self):
        # Test when num_collections is zero
        items = pd.Series([1, 2, 3])
        num_collections = 0
        with self.assertRaises(ValueError):
            collections = items_to_distributed_sublists(items, num_collections)

if __name__ == "__main__":
    unittest.main(verbosity=2)