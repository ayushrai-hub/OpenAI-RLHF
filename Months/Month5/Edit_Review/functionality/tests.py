import unittest
from unittest.mock import patch, mock_open, Mock
import os
from ideal_completion import fetch_codegen_output, write_code_to_file, run_code_from_file

class TestIdealCompletion(unittest.TestCase):

    @patch('ideal_completion.requests.post')
    def test_fetch_codegen_output_success(self, mock_post):
        # Test for successful API response when fetching code
        mock_response = Mock()
        expected_code = 'def hello_world():\n    print("Hello, World!")'
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': expected_code
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        prompt_input = 'Write a hello world program in Python'
        code = fetch_codegen_output(prompt_input)

        self.assertEqual(code, expected_code)

    @patch('ideal_completion.requests.post')
    def test_fetch_codegen_output_api_error(self, mock_post):
        # Test for API request failure (exception raised)
        mock_post.side_effect = Exception('API Error')

        prompt_input = 'Write a hello world program in Python'
        code = fetch_codegen_output(prompt_input)

        self.assertIsNone(code)

    @patch('builtins.open', new_callable=mock_open)
    def test_write_code_to_file_success(self, mock_file):
        # Test for successful code writing to a file
        python_filename = 'test_script.py'
        python_code = 'print("Test")'

        write_code_to_file(python_filename, python_code)

        mock_file.assert_called_with(python_filename, 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with(python_code)

    @patch('builtins.open', new_callable=mock_open)
    def test_write_code_to_file_unicode_error(self, mock_file):
        # Test for handling Unicode encoding error during file write
        mock_file.side_effect = UnicodeEncodeError('utf-8', 'test', 0, 1, 'reason')

        python_filename = 'test_script.py'
        python_code = 'print("Test")'

        write_code_to_file(python_filename, python_code)
        # Exception is handled internally; no assertion necessary

    @patch('ideal_completion.subprocess.run')
    def test_run_code_from_file_success(self, mock_run):
        # Test for successful execution of code from a file
        python_filename = 'test_script.py'

        run_code_from_file(python_filename)

        mock_run.assert_called_with(['python', python_filename], check=True)

    @patch('ideal_completion.subprocess.run')
    def test_run_code_from_file_non_python_extension(self, mock_run):
        # Test to ensure code is not run if the file has a non-Python extension
        python_filename = 'test_script.txt'

        run_code_from_file(python_filename)

        mock_run.assert_not_called()

    @patch('ideal_completion.subprocess.run')
    def test_run_code_from_file_execution_error(self, mock_run):
        # Test for handling execution errors when running code from a file
        mock_run.side_effect = Exception('Execution Error')

        python_filename = 'test_script.py'

        run_code_from_file(python_filename)
        # Exception is handled internally; no assertion necessary

if __name__ == '__main__':
    unittest.main(verbosity=2)
