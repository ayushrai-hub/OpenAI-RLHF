import unittest
import random
from testable_ideal_code import (
    bubble_organize, selection_organize, insertion_organize,
    merge_organize, quick_organize, heap_organize,
    radix_organize, counting_organize, shell_organize
)

class TestSortingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.sorting_functions = [
            bubble_organize, selection_organize, insertion_organize,
            merge_organize, quick_organize, heap_organize,
            radix_organize, counting_organize, shell_organize
        ]
    # It verifies that sorting algorithms correctly handle empty lists.
    def test_empty_list(self):
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                self.assertEqual(sort_func([]), [])
    # This test checks if algorithms properly handle lists with only one element.
    def test_single_element_list(self):
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                self.assertEqual(sort_func([1]), [1])
    # This test ensures algorithms don't alter an already sorted list
    def test_already_sorted_list(self):
        sorted_list = list(range(100))
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                self.assertEqual(sort_func(sorted_list.copy()), sorted_list)
    # THis tests algorithms with a completely reversed list
    def test_reverse_sorted_list(self):
        reverse_sorted = list(range(100, 0, -1))
        sorted_list = list(range(1, 101))
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                self.assertEqual(sort_func(reverse_sorted.copy()), sorted_list)
    # This test verifies sorting correctness with a large, randomly generated list
    def test_random_list(self):
        random_list = [random.randint(1, 1000) for _ in range(1000)]
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                sorted_result = sort_func(random_list.copy())
                self.assertEqual(sorted_result, sorted(random_list))
    # This tests how algorithms handle lists containing duplicate elements
    def test_list_with_duplicates(self):
        list_with_duplicates = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        expected_result = [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
        for sort_func in self.sorting_functions:
            with self.subTest(sort_func=sort_func.__name__):
                self.assertEqual(sort_func(list_with_duplicates.copy()), expected_result)

if __name__ == '__main__':
    unittest.main(verbosity=2)