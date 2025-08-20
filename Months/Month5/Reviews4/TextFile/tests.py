import unittest
from unittest.mock import patch, mock_open
from testableIC import extract_numbers_from_string

class TestExtractNumbers(unittest.TestCase):
    
    @patch('builtins.open', new_callable=mock_open, read_data='acascsca12341212asdavhjtmtyntyn123141212gt4g4tgtgrtynt7685334424sdvsdvd')
    def test_extract_numbers_valid(self, mock_file):
        # Simulate reading from 'file.txt'
        with open('file.txt', 'r') as file:
            data = file.read().strip()
        expected_output = [12341212, 123141212, 4, 4, 7685334424]
        self.assertEqual(extract_numbers_from_string(data), expected_output)

    @patch('builtins.open', new_callable=mock_open, read_data='no numbers here!')
    def test_extract_numbers_no_numbers(self, mock_file):
        # Simulate reading from 'file.txt'
        with open('file.txt', 'r') as file:
            data = file.read().strip()
        expected_output = []
        self.assertEqual(extract_numbers_from_string(data), expected_output)

if __name__ == '__main__':
    unittest.main()
