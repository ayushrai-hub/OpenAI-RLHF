# File: test_nearest_point_finder.py

import unittest
from shapely.geometry import Point
import numpy
from original_code import find_nearest_index

class TestNearestPointFinder(unittest.TestCase):

    def setUp(self):
        self.points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]

    def test_basic_case(self):
        query_point = Point(1.5, 1.5)
        result = find_nearest_index(self.points, query_point)
        self.assertEqual(result, 1)

    def test_nearest_to_first_point(self):
        query_point = Point(0.1, 0.1)
        result = find_nearest_index(self.points, query_point)
        self.assertEqual(result, 0)

    def test_nearest_to_last_point(self):
        query_point = Point(2.9, 2.9)
        result = find_nearest_index(self.points, query_point)
        self.assertEqual(result, 3)

    def test_single_point(self):
        single_point = [Point(0, 0)]
        query_point = Point(1, 1)
        result = find_nearest_index(single_point, query_point)
        self.assertEqual(result, 0)

    def test_duplicate_points(self):
        points_with_duplicate = [Point(0, 0), Point(0, 0)]
        query_point = Point(0, 0)
        result = find_nearest_index(points_with_duplicate, query_point)
        self.assertIn(result, [0, 1])

    def test_large_dataset(self):
        import random
        large_points = [Point(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(1000)]
        query_point = Point(50, 50)
        result = find_nearest_index(large_points, query_point)

        print(f"Type of result: {type(result)}")
        print(f"Value of result: {result}")

        self.assertIsInstance(result, (int, numpy.int64))

        self.assertTrue(0 <= result < 1000)

if __name__ == '__main__':
    unittest.main(verbosity=2)