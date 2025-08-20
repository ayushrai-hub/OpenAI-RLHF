import unittest
from typing import List
from testable_ideal_solution import (
    sequence_expander,
    is_basic_sequence,
    expand_range,
    broaden_basic_sequence,
    broaden_complex_sequence,
    ensure_structure
)

class TestSequenceExpander(unittest.TestCase):
    def test_is_basic_sequence(self):
        """Test basic sequence detection"""
        # Verify that numeric sequences are correctly identified as basic
        self.assertTrue(is_basic_sequence("1", "5"))
        # Verify that alphabetic sequences are correctly identified as basic
        self.assertTrue(is_basic_sequence("a", "z"))
        # Verify that mixed type sequences are correctly identified as non-basic
        self.assertFalse(is_basic_sequence("1", "z"))
        self.assertFalse(is_basic_sequence("a", "9"))
        # Verify that dot-notation sequences are identified as non-basic
        self.assertFalse(is_basic_sequence("1.1", "1.5"))

    def test_expand_range_numeric(self):
        """Test numeric range expansion"""
        # Verify standard numeric range expansion works correctly
        self.assertEqual(list(expand_range("1", "5")), ["1", "2", "3", "4", "5"])
        # Verify ranges starting from zero work correctly
        self.assertEqual(list(expand_range("0", "3")), ["0", "1", "2", "3"])
        # Verify single number ranges work correctly
        self.assertEqual(list(expand_range("7", "7")), ["7"])
        # Verify that invalid ranges (end < start) raise appropriate error
        with self.assertRaises(ValueError):
            list(expand_range("5", "1"))

    def test_expand_range_alphabetic(self):
        """Test alphabetic range expansion"""
        # Verify standard alphabetic range expansion works correctly
        self.assertEqual(list(expand_range("a", "d")), ["a", "b", "c", "d"])
        # Verify ranges near alphabet end work correctly
        self.assertEqual(list(expand_range("x", "z")), ["x", "y", "z"])
        # Verify single letter ranges work correctly
        self.assertEqual(list(expand_range("m", "m")), ["m"])
        # Verify that reverse alphabetic ranges raise appropriate error
        with self.assertRaises(ValueError):
            list(expand_range("z", "a"))

    def test_expand_range_invalid_input(self):
        """Test invalid input handling for range expansion"""
        # Verify that mixing numbers and letters raises error
        with self.assertRaises(ValueError):
            list(expand_range("1", "a"))
        with self.assertRaises(ValueError):
            list(expand_range("a", "1"))
        # Verify that non-alphanumeric characters raise error
        with self.assertRaises(ValueError):
            list(expand_range("!", "@"))

    def test_broaden_basic_sequence(self):
        """Test basic sequence broadening"""
        # Verify numeric sequence broadening works correctly
        self.assertEqual(broaden_basic_sequence("1", "3"), ["1", "2", "3"])
        # Verify alphabetic sequence broadening works correctly
        self.assertEqual(broaden_basic_sequence("a", "c"), ["a", "b", "c"])
        # Verify invalid sequences raise appropriate errors
        with self.assertRaises(ValueError):
            broaden_basic_sequence("3", "1")
        with self.assertRaises(ValueError):
            broaden_basic_sequence("z", "a")

    def test_broaden_complex_sequence(self):
        """Test complex sequence broadening"""
        # Verify numeric dot notation sequence expansion works correctly
        self.assertEqual(
            broaden_complex_sequence("1.1", "1.3"),
            ["1.1", "1.2", "1.3"]
        )
        # Verify mixed alpha-numeric dot notation works correctly
        self.assertEqual(
            broaden_complex_sequence("a.1", "a.3"),
            ["a.1", "a.2", "a.3"]
        )
        # Verify mismatched component counts raise error
        with self.assertRaises(ValueError):
            broaden_complex_sequence("1.1", "1.1.1")
        # Verify mismatched component types raise error
        with self.assertRaises(ValueError):
            broaden_complex_sequence("1.a", "1.1")

    def test_ensure_structure(self):
        """Test structure validation"""
        # Verify valid numeric structures are accepted
        ensure_structure(["1", "1"], ["1", "3"], "1.1", "1.3")
        # Verify valid mixed alpha-numeric structures are accepted
        ensure_structure(["a", "1"], ["a", "3"], "a.1", "a.3")  
        # Verify different component counts raise error
        with self.assertRaises(ValueError):
            ensure_structure(["1"], ["1", "1"], "1", "1.1")
        # Verify mismatched component types raise error
        with self.assertRaises(ValueError):
            ensure_structure(["1", "a"], ["1", "1"], "1.a", "1.1")

    def test_sequence_expander_basic(self):
        """Test main function with basic sequences"""
        # Verify basic numeric sequence expansion works end-to-end
        self.assertEqual(sequence_expander("1", "3"), ["1", "2", "3"])
        # Verify basic alphabetic sequence expansion works end-to-end
        self.assertEqual(sequence_expander("x", "z"), ["x", "y", "z"])
        # Verify single-element sequences work correctly
        self.assertEqual(sequence_expander("5", "5"), ["5"])
        self.assertEqual(sequence_expander("m", "m"), ["m"])

    def test_sequence_expander_complex(self):
        """Test main function with complex sequences"""
        # Verify complex numeric sequence expansion works end-to-end
        self.assertEqual(
            sequence_expander("1.1", "1.3"),
            ["1.1", "1.2", "1.3"]
        )
        # Verify complex alpha-numeric sequence expansion works end-to-end
        self.assertEqual(
            sequence_expander("a.1", "a.3"),
            ["a.1", "a.2", "a.3"]
        )

    def test_sequence_expander_edge_cases(self):
        """Test edge cases and error conditions"""
        # Verify invalid ranges raise appropriate errors
        with self.assertRaises(ValueError):
            sequence_expander("3", "1")
        with self.assertRaises(ValueError):
            sequence_expander("z", "a")
        # Verify type mismatches raise appropriate errors
        with self.assertRaises(ValueError):
            sequence_expander("1", "a")
        with self.assertRaises(ValueError):
            sequence_expander("1.a", "1.1")
        # Verify structural mismatches raise appropriate errors
        with self.assertRaises(ValueError):
            sequence_expander("1.1", "1.1.1")

if __name__ == '__main__':
    unittest.main(verbosity=2)