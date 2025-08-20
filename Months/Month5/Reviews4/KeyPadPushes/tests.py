from testableIc import Solution
import unittest

class TestSolution(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_example_1(self):
        word = "abcde"
        expected_output = 5
        self.assertEqual(self.solution.minimumPushes(word), expected_output)

    def test_example_2(self):
        word = "xyzxyzxyzxyz"
        expected_output = 12
        self.assertEqual(self.solution.minimumPushes(word), expected_output)

    def test_example_3(self):
        word = "aabbccddeeffgghhiiiiii"
        expected_output = 24
        self.assertEqual(self.solution.minimumPushes(word), expected_output)

    def test_case_empty_string(self):
        word = ""
        expected_output = 0
        self.assertEqual(self.solution.minimumPushes(word), expected_output)

    def test_case_single_character(self):
        word = "a"
        expected_output = 1
        self.assertEqual(self.solution.minimumPushes(word), expected_output)

if __name__ == "__main__":
    unittest.main(verbosity=2)