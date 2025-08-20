import unittest
import socket
from unittest.mock import patch, MagicMock, mock_open
import os

# Importing the functions from the main script
from testableIC import listen_and_receive_large_message, send_large_message


class TestFileTransfer(unittest.TestCase):

    @patch('socket.socket')
    @patch('builtins.open', new_callable=mock_open)
    def test_listen_and_receive_large_message(self, mock_file, mock_socket):
        """Test the receive function by mocking socket and file operations."""
        # Set up the mock socket to simulate data reception
        mock_conn = MagicMock()
        mock_conn.recv.side_effect = [b'data_chunk1', b'data_chunk2', b'']  # Simulating chunks of data then EOF
        
        mock_socket.return_value.__enter__.return_value.accept.return_value = (mock_conn, ('127.0.0.1', 12345))

        # Call the function to test
        listen_and_receive_large_message('output_file.bin', '127.0.0.1', 65432, 1024)

        # Ensure that the file was opened in write mode and data was written
        mock_file.assert_called_once_with('output_file.bin', 'wb')
        mock_file().write.assert_any_call(b'data_chunk1')
        mock_file().write.assert_any_call(b'data_chunk2')
        self.assertEqual(mock_file().write.call_count, 2)

    @patch('socket.socket')
    @patch('builtins.open', new_callable=mock_open, read_data=b'data_chunk1data_chunk2')
    def test_send_large_message(self, mock_file, mock_socket):
        """Test the send function by mocking socket and file operations."""
        # Set up the mock socket to simulate sending data
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        # Call the function to test
        send_large_message('large_file.bin', '127.0.0.1', 65432, 1024)

        # Ensure that the file was opened in read mode and data was sent via socket
        mock_file.assert_called_once_with('large_file.bin', 'rb')
        mock_sock.sendall.assert_any_call(b'data_chunk1data_chunk2')

    @patch('os.path.exists')
    def test_send_large_message_file_not_exist(self, mock_exists):
        """Test the send function when the file does not exist."""
        # Set the mock to return False, simulating a missing file
        mock_exists.return_value = False

        # Call the function and ensure it does not try to open a file that does not exist
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            send_large_message('non_existent_file.bin', '127.0.0.1', 65432, 1024)
            mock_file.assert_not_called()

    @patch('os.path.getsize', return_value=1024 * 1024 * 100)  # Mock file size to 100MB
    @patch('socket.socket')
    @patch('builtins.open', new_callable=mock_open, read_data=b'data' * 1024 * 1024 * 50)
    def test_large_file_send_progress(self, mock_file, mock_socket, mock_getsize):
        """Test that progress logging for large files occurs every 50 MB."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        with patch('builtins.print') as mock_print:
            send_large_message('large_file.bin', '127.0.0.1', 65432, 1024 * 64)
        
            # Test if print is called for each 50MB progress
            mock_print.assert_any_call("Sent 50 MB...")
            mock_print.assert_any_call("Sent 100 MB...")

    @patch('socket.socket')
    def test_listen_and_receive_socket_error(self, mock_socket):
        """Test that the receiver handles socket errors gracefully."""
        mock_socket.return_value.__enter__.side_effect = socket.error("Socket error")

        with patch('builtins.print') as mock_print:
            listen_and_receive_large_message('output_file.bin', '127.0.0.1', 65432, 1024)
            mock_print.assert_any_call("Error: Socket error")

if __name__ == "__main__":
    unittest.main(verbosity=2)