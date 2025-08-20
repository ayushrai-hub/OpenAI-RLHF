import unittest
from testableIC import Solution

class TestResultsArray(unittest.TestCase):
    
    def test_example_1(self):
        nums = [1,2,3,4,3,2,5]
        k = 3
        expected_output = [3,4,-1,-1,-1]
        solution = Solution()
        self.assertEqual(solution.resultsArray(nums, k), expected_output)

    def test_example_2(self):
        nums = [2,2,2,2,2]
        k = 4
        expected_output = [-1,-1]
        solution = Solution()
        self.assertEqual(solution.resultsArray(nums, k), expected_output)

    def test_example_3(self):
        nums = [3,2,3,2,3,2]
        k = 2
        expected_output = [-1,3,-1,3,-1]
        solution = Solution()
        self.assertEqual(solution.resultsArray(nums, k), expected_output)

    def test_example_4(self):
        nums = [1,2,3,4,5,6,7,8]
        k = 2
        expected_output = [2,3,4,5,6,7,8]
        solution = Solution()
        self.assertEqual(solution.resultsArray(nums, k), expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)
