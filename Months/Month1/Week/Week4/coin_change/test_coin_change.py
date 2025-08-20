import unittest
from io import StringIO
import sys
from unittest.mock import patch
import coin_change

class TestCodeChange(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def assert_stdout(self, input_value, expected_output, mock_stdout):
        with patch('builtins.input', return_value=str(input_value)):
            coin_change.main()
        self.assertEqual(mock_stdout.getvalue().strip(), expected_output)

    def test_no_change(self):
        self.assert_stdout(0, "No change")

    def test_only_pennies(self):
        self.assert_stdout(4, "4 Pennies")

    def test_only_nickel(self):
        self.assert_stdout(5, "1 Nickel")

    def test_only_dime(self):
        self.assert_stdout(10, "1 Dime")

    def test_only_quarter(self):
        self.assert_stdout(25, "1 Quarter")

    def test_mixed_coins(self):
        self.assert_stdout(41, "1 Quarter\n1 Dime\n1 Nickel\n1 Penny")

    def test_multiple_of_each(self):
        self.assert_stdout(99, "3 Quarters\n2 Dimes\n4 Pennies")

    def test_large_amount(self):
        self.assert_stdout(199, "7 Quarters\n2 Dimes\n4 Pennies")

if __name__ == '__main__':
    unittest.main(verbosity=2)