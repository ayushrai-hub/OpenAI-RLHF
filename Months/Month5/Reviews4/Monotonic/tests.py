import unittest
from testableIC import count_monotonic_pairs

class TestCountMonotonicPairs(unittest.TestCase):
    
    def test_single_element(self):
        nums = [10]
        expected_output = 11
        result = count_monotonic_pairs(nums)
        self.assertEqual(result, expected_output)

    def test_all_equal_elements(self):
        nums = [2, 2, 2]
        expected_output = 10
        result = count_monotonic_pairs(nums)
        self.assertEqual(result, expected_output)

    def test_example_case_1(self):
        nums = [2, 3, 2]
        expected_output = 4
        result = count_monotonic_pairs(nums)
        self.assertEqual(result, expected_output)

    def test_example_case_2(self):
        nums = [3,21]
        expected_output = 10
        result = count_monotonic_pairs(nums)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)