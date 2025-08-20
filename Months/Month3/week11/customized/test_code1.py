import unittest
from unittest.mock import patch
from io import StringIO
from IPython.display import display
# Assuming the original code is in a file named ideal_completion.py
from testable_ideal_code import greeting_program

class TestGreetingProgram(unittest.TestCase):
    @patch('builtins.input', return_value='John Doe')
    @patch('sys.stdout', new_callable=StringIO)
    def test_greeting_program_output(self, mock_stdout, mock_input):
        # This test verifies that the program correctly processes a full name input and returns the expected greeting message. 
        result = greeting_program()
        expected_output = "Hi John! I'm Mike, pleased to meet you."
        self.assertEqual(result, expected_output)

    @patch('builtins.input', return_value='Alice Wonder')
    def test_greeting_program_return(self, mock_input):
        # This test checks if the function returns the correct greeting string.
        result = greeting_program()
        expected_output = "Hi Alice! I'm Mike, pleased to meet you."
        self.assertEqual(result, expected_output)

    @patch('builtins.input', return_value='Bob')
    def test_greeting_program_single_name(self, mock_input):
        # This test ensures the program handles single-name inputs correctly.
        result = greeting_program()
        expected_output = "Hi Bob! I'm Mike, pleased to meet you."
        self.assertEqual(result, expected_output)

    @patch('builtins.input', return_value='Charlie Chaplin Jr.')
    def test_greeting_program_multiple_names(self, mock_input):
        # This test checks if the program correctly handles names with more than two parts.
        result = greeting_program()
        expected_output = "Hi Charlie! I'm Mike, pleased to meet you."
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main(verbosity=2)