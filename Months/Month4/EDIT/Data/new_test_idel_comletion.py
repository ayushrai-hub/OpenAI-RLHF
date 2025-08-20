import unittest
from unittest.mock import MagicMock
import threading
import json
from ideal_completion import handle_client, broadcast_positions, players, connections, lock


class TestServer(unittest.TestCase):
    def setUp(self):
        """Reset shared state before each test."""
        with lock:
            self.players = {10009, 10004, 10000, 10010}
            connections.clear()

    def tearDown(self):
        """Clean up after each test."""
        with lock:
            players.clear()
            connections.clear()

    def test_handle_client_move_request(self):
        """Test handling of move request packets."""
        mock_conn = MagicMock()
        mock_conn.recv = MagicMock(side_effect=[
            json.dumps({"type": "move_request", "target": [10.0, 20.0]}).encode('utf-8'),
            b''
        ])
        addr = ('127.0.0.1', 10000)

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        thread.join()

        with lock:
            self.assertIn(10000, self.players)
            self.assertEqual(players[10000]['position'], [10.0, 20.0])
            self.assertTrue(players[10000]['moving'])

    def test_handle_client_invalid_json(self):
        """Test handling of invalid JSON data."""
        mock_conn = MagicMock()
        mock_conn.recv = MagicMock(side_effect=[b'{"type": "update", "position": [15, 25', b''])
        addr = ('127.0.0.1', 10004)

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        thread.join()

        with lock:
            self.assertIn(10004, self.players)
            self.assertEqual(players[10004]['position'], [0, 0])  # Default position
            self.assertFalse(players[10004]['moving'])

    def test_handle_client_concurrent_access(self):
        """Test thread safety with concurrent client access."""
        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()

        mock_conn1.recv = MagicMock(side_effect=[
            json.dumps({"type": "update", "position": [10.0, 20.0]}).encode('utf-8'),
            b''
        ])
        mock_conn2.recv = MagicMock(side_effect=[
            json.dumps({"type": "update", "position": [30.0, 40.0]}).encode('utf-8'),
            b''
        ])

        addr1 = ('127.0.0.1', 10009)
        addr2 = ('127.0.0.1', 10010)

        thread1 = threading.Thread(target=handle_client, args=(mock_conn1, addr1))
        thread2 = threading.Thread(target=handle_client, args=(mock_conn2, addr2))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        with lock:
            self.assertIn(10009, self.players)
            self.assertIn(10010, self.players)
            self.assertEqual(players[10009]['position'], [10.0, 20.0])
            self.assertEqual(players[10010]['position'], [30.0, 40.0])

    def test_broadcast_positions(self):
        """Test broadcasting positions to all clients."""
        with lock:
            players[10006] = {'position': [10.0, 20.0], 'moving': True}
            players[10007] = {'position': [15.0, 25.0], 'moving': False}

        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()
        with lock:
            connections.extend([mock_conn1, mock_conn2])

        broadcast_positions()

        expected_message = json.dumps({
            "type": "sync",
            "players": [
                {"player_id": 10006, "position": [10.0, 20.0], "moving": True},
                {"player_id": 10007, "position": [15.0, 25.0], "moving": False}
            ]
        }).encode('utf-8')

        mock_conn1.sendall.assert_called_with(expected_message)
        mock_conn2.sendall.assert_called_with(expected_message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
