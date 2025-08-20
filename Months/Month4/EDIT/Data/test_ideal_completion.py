import unittest
from unittest.mock import MagicMock
import threading
from ideal_completion import handle_client, broadcast_positions, players, connections, lock
import json

class TestServer(unittest.TestCase):

    def setUp(self):
        # Reset the shared data structures before each test
        players.clear()
        connections.clear()

    def test_handle_client_move_request(self):
        # Create a mock socket connection
        mock_conn = MagicMock()
        # Simulate the client's move_request packet
        data = json.dumps({
            "type": "move_request",
            "target": [10, 20]
        }).encode('utf-8')
        # Mock the recv method to return the packet and then terminate
        mock_conn.recv = MagicMock(side_effect=[data, b''])
        addr = ('127.0.0.1', 10000)

        # Start the handle_client function in a thread
        client_thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        client_thread.start()
        client_thread.join()

        # Verify that the player's position and moving status are updated
        self.assertIn(10000, players)
        self.assertEqual(players[10000]['position'], [10, 20])
        self.assertTrue(players[10000]['moving'])

    def test_handle_client_update(self):
        # Initialize player's data
        players[10001] = {'position': (0, 0), 'moving': True}

        # Create a mock socket connection
        mock_conn = MagicMock()
        # Simulate the client's update packet
        data = json.dumps({
            "type": "update",
            "position": [15, 25]
        }).encode('utf-8')
        # Mock the recv method
        mock_conn.recv = MagicMock(side_effect=[data, b''])
        addr = ('127.0.0.1', 10001)

        # Start the handle_client function
        client_thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        client_thread.start()
        client_thread.join()

        # Verify that the player's position is updated
        self.assertEqual(players[10001]['position'], [15, 25])

    def test_broadcast_positions(self):
        # Add test players
        players[10000] = {'position': [10, 20], 'moving': True}
        players[10001] = {'position': [15, 25], 'moving': False}

        # Create mock connections
        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()
        connections.extend([mock_conn1, mock_conn2])

        # Call the broadcast_positions function
        broadcast_positions()

        # Expected message
        expected_message = json.dumps({
            "type": "sync",
            "players": [
                {"player_id": 10000, "position": [10, 20], "moving": True},
                {"player_id": 10001, "position": [15, 25], "moving": False}
            ]
        }).encode('utf-8')

        # Verify that sendall was called with the correct message
        mock_conn1.sendall.assert_called_with(expected_message)
        mock_conn2.sendall.assert_called_with(expected_message)

    def test_handle_client_disconnect(self):
        # Create a mock socket connection
        mock_conn = MagicMock()
        # Simulate client disconnection
        mock_conn.recv = MagicMock(return_value=b'')
        addr = ('127.0.0.1', 10002)

        # Start the handle_client function
        client_thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        client_thread.start()
        client_thread.join()

        # Verify that the player is removed and connection is closed
        self.assertNotIn(10002, players)
        mock_conn.close.assert_called_once()

    def test_handle_client_invalid_json(self):
        # Create a mock socket connection
        mock_conn = MagicMock()
        # Simulate invalid JSON data
        data = b'{"type": "update", "position": [15, 25}'  # Missing closing brace
        mock_conn.recv = MagicMock(side_effect=[data, b''])
        addr = ('127.0.0.1', 10003)

        # Start the handle_client function
        client_thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        client_thread.start()
        client_thread.join()

        # Verify that the player's data was not updated due to JSON error
        self.assertIn(10003, players)
        self.assertEqual(players[10003]['position'], (0, 0))

if __name__ == '__main__':
    unittest.main()
