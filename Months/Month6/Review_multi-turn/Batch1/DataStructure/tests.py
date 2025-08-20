from ideal_completion import EvenOccurrenceChecker
import unittest

class TestEvenOccurrenceChecker(unittest.TestCase):
    def test_basic_functionality(self):
        # This tests the core functionality of the EvenOccurrenceChecker class.
        self.nums = [1, 2, 1, 2, 3, 3, 4, 4]
        checker = EvenOccurrenceChecker(self.nums)
        
        # It verifies the ranges where all elements appear an even number of time.
        self.assertTrue(checker.query_range(0, 3))  # [1,2,1,2]
        self.assertTrue(checker.query_range(4, 7))  # [3,3,4,4]
        
        # It verifies the ranges where at least one element appears an odd number of time.
        self.assertFalse(checker.query_range(2, 5))  # [1,2,3,3]
        self.assertFalse(checker.query_range(1, 4))  # [2,1,2,3]

    def test_edge_cases(self):
        # It tests the boundary conditions and extreme scenarios to ensure robust behavior.
        min_checker = EvenOccurrenceChecker([1, 1])
        self.assertTrue(min_checker.query_range(0, 1))
        
        # It tests the array with maximum allowed unique elements (64).
        max_nums = list(range(32)) * 2  # 64 elements, 32 unique
        max_checker = EvenOccurrenceChecker(max_nums)
        self.assertTrue(max_checker.query_range(0, 63))

    def test_invalid_inputs(self):
        # It tests the error handling for various invalid inputs to ensure proper validation.
        checker = EvenOccurrenceChecker([1, 2, 3, 4])
        
        # It verifies the empty array rejection.
        with self.assertRaises(ValueError):
            EvenOccurrenceChecker([])
        
        # it tests the various invalid range scenarios.
        with self.assertRaises(ValueError):
            checker.query_range(-1, 2)  # negative index
        with self.assertRaises(ValueError):
            checker.query_range(0, 4)   # index out of bounds
        with self.assertRaises(ValueError):
            checker.query_range(2, 1)   # left > right
        
        # It tests odd length range rejection.
        with self.assertRaises(ValueError):
            checker.query_range(0, 2)   # length = 3 (odd)

    def test_too_many_unique_elements(self):
        # It tests the unique elements limit constrints.
        large_nums = list(range(65))  # 65 unique elements
        with self.assertRaises(ValueError):
            EvenOccurrenceChecker(large_nums)

    def test_complex_patterns(self):
        # It tests more sophisticated element patterns to ensure correct counting logic,
        nums = [1, 1, 2, 2, 3, 3, 4, 4]
        checker = EvenOccurrenceChecker(nums)
        
        # It tests the overlapping ranges with even occurrences
        self.assertTrue(checker.query_range(0, 3))   # [1,1,2,2]
        self.assertTrue(checker.query_range(2, 5))   # [2,2,3,3]
        self.assertTrue(checker.query_range(4, 7))   # [3,3,4,4]
        
        # It tests the overlapping ranges with odd occurrences
        self.assertFalse(checker.query_range(1, 4))  # [1,2,2,3]
        self.assertFalse(checker.query_range(3, 6))  # [2,3,3,4]

    def test_repeated_elements(self):
        # It tests scenarios wiht multiple repetitions of the same elements.
        nums = [1, 1, 1, 1, 2, 2, 2, 2]
        checker = EvenOccurrenceChecker(nums)
        
        # It tests various ranges with repeated elements.
        self.assertTrue(checker.query_range(0, 3))   # [1,1,1,1]
        self.assertTrue(checker.query_range(4, 7))   # [2,2,2,2]
        self.assertTrue(checker.query_range(2, 5))   # [1,1,2,2]
        self.assertFalse(checker.query_range(1, 4))  # [1,1,1,2]

if __name__ == '__main__':
    unittest.main(verbosity=2)