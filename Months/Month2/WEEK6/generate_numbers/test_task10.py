import unittest
from io import StringIO
import sys

# Assume the above function is in a file named 'number_generator.py'
from code10 import generate_numbers

class TestGenerateNumbers(unittest.TestCase):

    def test_output_length(self):
        """Test if the function generates the correct number of results."""
        self.assertEqual(len(generate_numbers(10)), 10)
        self.assertEqual(len(generate_numbers(0)), 0)
        self.assertEqual(len(generate_numbers(100)), 100)

    def test_binary_decimal_correspondence(self):
        """Test if binary and decimal results correspond correctly."""
        results = generate_numbers(10)
        for i, (binary, decimal) in enumerate(results):
            self.assertEqual(int(binary), decimal)
            self.assertEqual(decimal, i % 2)

    def test_alternating_pattern(self):
        """Test if the results alternate correctly between 0 and 1."""
        results = generate_numbers(10)
        for i in range(0, 10, 2):
            self.assertEqual(results[i], ('0', 0))
        for i in range(1, 10, 2):
            self.assertEqual(results[i], ('1', 1))



if __name__ == '__main__':
    unittest.main(verbosity=2)