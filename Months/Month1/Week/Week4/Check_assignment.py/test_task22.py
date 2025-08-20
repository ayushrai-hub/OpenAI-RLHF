import unittest
from io import StringIO
import sys

# Assuming the function is in a file named number_pattern.py
from original_code import print_number_pattern

class TestNumberPattern(unittest.TestCase):
    def capture_output(self, n):
        captured_output = StringIO()
        sys.stdout = captured_output
        print_number_pattern(n)
        sys.stdout = sys.__stdout__
        return captured_output.getvalue().strip()

    def test_pattern_3(self):
        expected_output = "13\n24\n35"
        self.assertEqual(self.capture_output(3), expected_output)

    def test_pattern_5(self):
        expected_output = "15\n26\n37\n48\n59"
        self.assertEqual(self.capture_output(5), expected_output)

    def test_pattern_1(self):
        expected_output = "11"
        self.assertEqual(self.capture_output(1), expected_output)

    def test_pattern_0(self):
        expected_output = ""
        self.assertEqual(self.capture_output(0), expected_output)

if __name__ == "__main__":
    unittest.main(verbosity=2)