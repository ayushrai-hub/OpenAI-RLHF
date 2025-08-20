# File: test_strtree_nearest_index.py

import unittest
from shapely.geometry import Point
from original_code import find_nearest_index

class TestSTRtreeNearestIndex(unittest.TestCase):
    def setUp(self):
        self.points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]

    def test_nearest_point(self):
        query_point = Point(1.5, 1.5)
        nearest_index = find_nearest_index(self.points, query_point)
        self.assertEqual(nearest_index, 1)  # Expecting Point(1, 1) to be nearest

    def test_exact_point(self):
        query_point = Point(2, 2)
        nearest_index = find_nearest_index(self.points, query_point)
        self.assertEqual(nearest_index, 2)  # Expecting Point(2, 2) to be nearest

    def test_out_of_range_point(self):
        query_point = Point(10, 10)
        nearest_index = find_nearest_index(self.points, query_point)
        self.assertEqual(nearest_index, 3)  # Expecting Point(3, 3) to be nearest

    def test_negative_coordinates(self):
        query_point = Point(-1, -1)
        nearest_index = find_nearest_index(self.points, query_point)
        self.assertEqual(nearest_index, 0)  # Expecting Point(0, 0) to be nearest

    def test_empty_points_list(self):
        query_point = Point(0, 0)
        with self.assertRaises(ValueError):
            find_nearest_index([], query_point)

if __name__ == '__main__':
    unittest.main(verbosity=2)