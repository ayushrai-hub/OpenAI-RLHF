import os
import unittest
from ideal_completion import remove_isolated_true

class TestIsolatedTrue(unittest.TestCase):

    def test_removal_of_consecutive_trues(self):
        arr = [False, False, False, True, True, False, False, True, True, True, False, False, True, False]
        res = remove_isolated_true(arr)
        expected = [False, False, False, True, False, False, True, False, False, True, False]
        self.assertEqual(res, expected)

    def test_num_of_falses(self):
        arr = [False, False, False, True, True, False, False, True, True, True, False, False, True, False]
        res = remove_isolated_true(arr)
        expected_false = arr.count(False)
        self.assertEqual(res.count(False), expected_false)

if __name__ == '__main__':
    unittest.main(verbosity=2)