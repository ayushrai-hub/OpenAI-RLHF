import unittest
from io import StringIO
import sys

# Assuming the original code is in a file named 'spaghetti_converter.py'
import spaghetti_converter
class TestSpaghettiConverter(unittest.TestCase):
    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        sys.stdout = self.held

    def test_valid_integer_input(self):
        sys.stdin = StringIO("42\n")
        spaghetti_converter.main()
        output = sys.stdout.getvalue().strip()
        self.assertIn("Data type  =:  <class 'int'>", output)
        self.assertIn("Data value =:  42", output)

    def test_valid_float_input(self):
        sys.stdin = StringIO("3.14\n")
        spaghetti_converter.main()
        output = sys.stdout.getvalue().strip()
        self.assertIn("Data type  =:  <class 'float'>", output)
        self.assertIn("Data value =:  3.14", output)

    def test_invalid_input(self):
        sys.stdin = StringIO("not a number\n")
        with self.assertRaises(SystemExit):
            spaghetti_converter.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "Invalid input: Not a number.")

if __name__ == '__main__':
    unittest.main(verbosity=2)