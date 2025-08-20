import unittest

from testableIC import *


class TestPacificAtlantic(unittest.TestCase):

    def test_pacific_atlantic(self):
        heights = [
            [1, 2, 2, 3, 5],
            [3, 2, 3, 4, 4],
            [2, 4, 5, 3, 1],
            [6, 7, 1, 4, 5],
            [5, 1, 1, 2, 4]
        ]
        expected_output = [
            [0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]
        ]

        solution = Solution()

        actual_output = solution.pacificAtlantic(heights)

        self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()