import unittest
from unittest.mock import patch, MagicMock
import subprocess
import logging
from testableIC import execute_command_with_popen

class TestExecuteCommandWithPopen(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_execute_command_with_popen_success(self, mock_popen):
        # Mock the Popen object and its methods
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Mocked STDOUT", "Mocked STDERR")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        command = "echo Hello, World!"
        stdout, stderr, return_code = execute_command_with_popen(command, limit=5, shell_execution=True)

        # Assert that Popen was called with the correct arguments
        mock_popen.assert_called_with(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            env=None,
            universal_newlines=True
        )

        # Check that the output matches the mocked values
        self.assertEqual(stdout, "Mocked STDOUT")
        self.assertEqual(stderr, "Mocked STDERR")
        self.assertEqual(return_code, 0)

    @patch('subprocess.Popen')
    def test_execute_command_with_popen_timeout(self, mock_popen):
        # Mock a timeout scenario
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired(cmd="echo Hello", timeout=5)
        mock_popen.return_value = mock_process

        command = "echo Hello, World!"
        stdout, stderr, return_code = execute_command_with_popen(command, limit=5, shell_execution=True)

        # Check if it handled the timeout and returned the appropriate message
        self.assertEqual(stdout, "")
        self.assertIn("COMMAND_TIMED_OUT", stderr)
        self.assertNotEqual(return_code, 0)

    @patch('subprocess.Popen')
    def test_execute_command_with_popen_error(self, mock_popen):
        # Mock an error scenario (e.g., command not found)
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "Command not found")
        mock_process.returncode = 127  # Typically 'command not found' return code
        mock_popen.return_value = mock_process

        command = "non_existing_command"
        stdout, stderr, return_code = execute_command_with_popen(command, limit=5, shell_execution=True)

        # Check if it handled the error and returned the appropriate message
        self.assertEqual(stdout, "")
        self.assertIn("Command not found", stderr)
        self.assertEqual(return_code, 127)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
