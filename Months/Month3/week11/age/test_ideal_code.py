import unittest
from testable_ideal_code import identify_middle_sibling

class TestSiblingIdentifier(unittest.TestCase):
    def test_equal_ages(self):
        # This verifies that the function correctly handles ties for middle sibling
        self.assertEqual(set(identify_middle_sibling('X=Y', 'X<Z', 'Y<Z')), {'X', 'Y'})
        
        # This checks if the function correctly identifies all siblings as middle when they're the same age
        self.assertEqual(set(identify_middle_sibling('X=Y', 'Y=Z', 'X=Z')), {'X', 'Y', 'Z'})

    def test_three_siblings(self):
        # This verifies the core functionality of identifying the middle sibling
        self.assertEqual(set(identify_middle_sibling('X>Y', 'X<Z', 'Y<Z')), {'X'})
        
        # This ensures the function works correctly with various age relation combinations
        self.assertEqual(set(identify_middle_sibling('X<Y', 'X>Z', 'Y>Z')), {'X'})

    def test_invalid_input(self):
        # Test case with insufficient input (less than 3 siblings)
        # This checks if the function properly raises a ValueError for invalid input
        with self.assertRaises(ValueError):
            identify_middle_sibling('X>Y')  # Less than 3 siblings
        
        # Test case with invalid relation format
        # This ensures the function can detect and handle incorrect input formats
        with self.assertRaises(ValueError):
            identify_middle_sibling('X>Y', 'Y<Z', 'Z:X')  # Invalid relation format

if __name__ == '__main__':
    unittest.main(verbosity=2)