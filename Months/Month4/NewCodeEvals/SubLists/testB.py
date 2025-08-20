
# test.py
import unittest
import pandas as pd
from ideal_completion import items_to_distributed_sublists

class TestItemsToDistributedSublists(unittest.TestCase):
    def setUp(self):
        # Create a sample pandas Series to distribute
        self.items_to_distribute = pd.Series([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.num_collections = 3

    def test_balanced_distribution(self):
        # Test the balanced version
        collections = items_to_distributed_sublists(self.items_to_distribute, self.num_collections)
        
        # Ensure that collections are distributed
        self.assertEqual(len(collections), self.num_collections)
        self.assertEqual(sum(len(col) for col in collections), len(self.items_to_distribute))

        # Ensure that the distribution is more balanced
        sums = [col.sum() for col in collections]
        self.assertTrue(max(sums) - min(sums) <= 3, "Balanced distribution is not evenly distributed.")

    def test_edge_case_single_collection(self):
        # Test when there is only one collection
        collections = items_to_distributed_sublists(self.items_to_distribute, 1)
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0].sum(), self.items_to_distribute.sum())

    def test_edge_case_more_collections_than_items(self):
        # Test when there are more collections than items
        collections = items_to_distributed_sublists(self.items_to_distribute, len(self.items_to_distribute) + 2)
        self.assertEqual(len(collections), len(self.items_to_distribute) + 2)

        # Ensure all items are distributed and some collections may be empty
        self.assertEqual(sum(len(col) for col in collections), len(self.items_to_distribute))

    def test_invalid_num_collections(self):
        # Test when num_collections is zero or negative
        with self.assertRaises(ValueError):
            items_to_distributed_sublists(self.items_to_distribute, 0)
        with self.assertRaises(ValueError):
            items_to_distributed_sublists(self.items_to_distribute, -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)