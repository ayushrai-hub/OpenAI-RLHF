import unittest

from program import remove_values_no_greater_than_index, cap_sum_to, increasing_sequence_from

class TestFunctions(unittest.TestCase):
    def test_remove_values_no_greater_than_index(self):
        test_list = [3, 0, 5, 2, 4, 1]
        remove_values_no_greater_than_index(test_list)
        self.assertEqual(test_list, [3, 5])

    def test_increasing_sequence_from(self):
        test_list = [3, 1, 4, 1, 5, 9, 2, 6]
        result = increasing_sequence_from(1, test_list)
        self.assertEqual(result, [1, 4, 5, 9])

    def test_cap_sum_to(self):
        test_list = [3, 1, 4, 1, 5, 9, 2, 6]
        result = cap_sum_to(10, test_list)
        self.assertEqual(result, [1, 9])

if __name__ == "__main__":
    unittest.main(verbosity=2)