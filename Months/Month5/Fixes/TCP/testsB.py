import unittest
from unittest.mock import MagicMock
import threading
import json
import time
from ideal_completion import handle_client, broadcast_positions, players, connections, lock

class TestServer(unittest.TestCase):
    def setUp(self):
        """Reset shared state before each test."""
        with lock:
            players.clear()
            connections.clear()
    
    def wait_for_condition(self, condition_func, timeout=1):
        """Helper method to wait for a condition to be true."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with lock:
                if condition_func():
                    return True
            time.sleep(0.01)
        return False

    def test_handle_client_invalid_json(self):
        mock_conn = MagicMock()
        addr = ('127.0.0.1', 10003)

        # Send invalid JSON data
        invalid_data = b'{"type": "update", "position": [15, 25}'  # Invalid JSON
        mock_conn.recv = MagicMock(side_effect=[invalid_data, b''])

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        
        # Wait for player to be added
        def check_condition():
            return 10003 in players
        
        self.assertTrue(self.wait_for_condition(check_condition))
        
        # Verify player was added and maintained default position
        with lock:
            self.assertIn(10003, players)
            self.assertEqual(players[10003]['position'], [0, 0])
        
        thread.join(timeout=1)

    def test_handle_client_update(self):
        mock_conn = MagicMock()
        addr = ('127.0.0.1', 10001)
        
        # Set initial state
        with lock:
            players[10001] = {'position': [0, 0], 'moving': True}
            connections.append(mock_conn)

        data = json.dumps({
            "type": "update",
            "position": [15, 25]
        }).encode('utf-8')
        mock_conn.recv = MagicMock(side_effect=[data, b''])

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        
        def check_condition():
            return (10001 in players and 
                   players[10001]['position'] == [15, 25])
        
        self.assertFalse(self.wait_for_condition(check_condition))
        thread.join(timeout=1)

    def test_broadcast_positions(self):
        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()
        
        with lock:
            players[10000] = {'position': [10, 20], 'moving': True}
            players[10001] = {'position': [15, 25], 'moving': False}
            connections.extend([mock_conn1, mock_conn2])

        broadcast_positions()

        expected_message = {
            'type': 'sync',
            'players': [
                {'player_id': 10000, 'position': [10, 20], 'moving': True},
                {'player_id': 10001, 'position': [15, 25], 'moving': False}
            ]
        }
        
        # Check that both connections received the message
        for mock_conn in [mock_conn1, mock_conn2]:
            call_args = mock_conn.sendall.call_args[0][0]
            received_message = json.loads(call_args.decode('utf-8'))
            # Sort players by ID to ensure consistent comparison
            received_message['players'].sort(key=lambda x: x['player_id'])
            expected_message['players'].sort(key=lambda x: x['player_id'])
            self.assertEqual(received_message, expected_message)

    def test_handle_client_disconnect(self):
        mock_conn = MagicMock()
        mock_conn.recv = MagicMock(return_value=b'')
        addr = ('127.0.0.1', 10002)

        with lock:
            players[10002] = {'position': [0, 0], 'moving': False}
            connections.append(mock_conn)

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        thread.join(timeout=1)

        with lock:
            self.assertNotIn(10002, players)
            self.assertNotIn(mock_conn, connections)
        mock_conn.close.assert_called_once()

    def test_handle_client_invalid_json(self):
        mock_conn = MagicMock()
        addr = ('127.0.0.1', 10003)
        
        invalid_data = b'{"type": "update", "position": [15, 25}'  # Invalid JSON
        valid_data = json.dumps({
            "type": "update",
            "position": [0, 0]
        }).encode('utf-8')
        mock_conn.recv = MagicMock(side_effect=[invalid_data, valid_data, b''])

        thread = threading.Thread(target=handle_client, args=(mock_conn, addr))
        thread.start()
        
        def check_condition():
            return 10003 in players
        
        self.assertTrue(self.wait_for_condition(check_condition))
        thread.join(timeout=1)

        with lock:
            self.assertIn(10003, players)
            self.assertEqual(players[10003]['position'], [0, 0])

if __name__ == '__main__':
    unittest.main(verbosity=2)