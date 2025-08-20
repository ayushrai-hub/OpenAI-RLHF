import unittest
from testableIC import min_operations_to_zero

class TestMinOperationsToZero(unittest.TestCase):
    
    def test_case_1(self):
        test_cases = [(1, 3), (2, 4), (199999, 200000), (19, 84)]
        expected_results = [5, 6, 36, 263]
        self.assertEqual(min_operations_to_zero(4, test_cases), expected_results)
    
    def test_case_2(self):
        test_cases = [(101, 300), (24, 408), (10, 20001), (1, 200000), (1, 2)]
        expected_results = [1063, 2034, 170482, 2134293, 3]
        self.assertEqual(min_operations_to_zero(5, test_cases), expected_results)

if __name__ == '__main__':
    unittest.main(verbosity=2)