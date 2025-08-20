import unittest
import json
import threading
from unittest.mock import Mock, patch
from new_ideal import handle_client, broadcast_positions, players, connections, handle_packet

class TestGameServer(unittest.TestCase):
    def setUp(self):
        # It sets up clean state before each test.
        players.clear()
        connections.clear()
        
    def test_handle_move_request(self):
        # It tests handling of move request packets.
        player_id = 5000
        packet = {
            'type': 'move_request',
            'target': [10.0, 20.0]
        }
        
        handle_packet(player_id, packet)
        
        self.assertIn(player_id, players)
        self.assertEqual(players[player_id]['position'], [10.0, 20.0])
        self.assertTrue(players[player_id]['moving'])

    def test_handle_update(self):
        # It tests handling of position update packets.
        player_id = 5000
        players[player_id] = {'position': [0.0, 0.0], 'moving': True}
        
        packet = {
            'type': 'update',
            'position': [15.0, 25.0]
        }
        
        handle_packet(player_id, packet)
        
        self.assertEqual(players[player_id]['position'], [15.0, 25.0])
        self.assertTrue(players[player_id]['moving'])

    def test_handle_reached(self):
        # It tests handling of destination reached packets.
        player_id = 5000
        players[player_id] = {'position': [10.0, 20.0], 'moving': True}
        
        packet = {'type': 'reached'}
        handle_packet(player_id, packet)
        
        self.assertFalse(players[player_id]['moving'])

    def test_handle_path_blocked(self):
        # It tests handling of path blocked packets.
        player_id = 5000
        players[player_id] = {'position': [10.0, 20.0], 'moving': True}
        
        packet = {'type': 'path_blocked'}
        handle_packet(player_id, packet)
        
        self.assertFalse(players[player_id]['moving'])

    def test_broadcast_positions(self):
        # It tests broadcasting position updates to all clients.
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        connections.extend([mock_conn1, mock_conn2])
        
        players[5000] = {'position': [10.0, 20.0], 'moving': True}
        players[5001] = {'position': [30.0, 40.0], 'moving': False}
        
        broadcast_positions()
        
        # Verify each connection received the broadcast
        self.assertEqual(mock_conn1.sendall.call_count, 1)
        self.assertEqual(mock_conn2.sendall.call_count, 1)
        
        # Verify broadcast content
        expected_data = {
            'type': 'sync',
            'players': {
                '5000': {'position': [10.0, 20.0], 'moving': True},
                '5001': {'position': [30.0, 40.0], 'moving': False}
            }
        }
        
        actual_data = json.loads(mock_conn1.sendall.call_args[0][0].decode('utf-8'))
        self.assertEqual(actual_data, expected_data)

    def test_client_disconnection(self):
        # It test proper cleanup when a client disconnects.
        mock_conn = Mock()
        player_id = 5000
        
        players[player_id] = {'position': [10.0, 20.0], 'moving': True}
        connections.append(mock_conn)
        
        with patch('ideal_completion.broadcast_positions'):
            handle_client(mock_conn, ('127.0.0.1', player_id))
            
            self.assertNotIn(player_id, players)
            self.assertNotIn(mock_conn, connections)
            mock_conn.close.assert_called_once()

    def test_broadcast_handles_dead_connections(self):
        # It tests that broadcasting handles failed connections gracefully.
        good_conn = Mock()
        bad_conn = Mock()
        bad_conn.sendall.side_effect = Exception("Connection lost")
        
        connections.extend([good_conn, bad_conn])
        players[5000] = {'position': [10.0, 20.0], 'moving': True}
        
        broadcast_positions()
        
        self.assertIn(good_conn, connections)
        self.assertNotIn(bad_conn, connections)
        bad_conn.close.assert_called_once()

    def test_handle_invalid_packet(self):
        # It tests handling of invalid packet types.
        player_id = 5000
        players[player_id] = {'position': [10.0, 20.0], 'moving': True}
        
        packet = {'type': 'invalid_type'}
        handle_packet(player_id, packet)
        
        # Verify player state remained unchanged
        self.assertEqual(players[player_id]['position'], [10.0, 20.0])
        self.assertTrue(players[player_id]['moving'])

    def test_handle_client_invalid_json(self):
        # It tests handling of malformed JSON data from client.
        mock_conn = Mock()
        addr = ('127.0.0.1', 5000)
        
        mock_conn.recv.side_effect = [
            b'{"type": "move_request", "target": [10.0, 20.0]',  # Incomplete JSON
            b'not a json packet',  # Invalid JSON
            b''  # Disconnect
        ]
        
        handle_client(mock_conn, addr)
        
        self.assertNotIn(5000, players)
        mock_conn.close.assert_called_once()

    def test_complete_client_flow(self):
        # It tests complete client flow including connection, packet handling, and disconnection.
        mock_conn = Mock()
        addr = ('127.0.0.1', 5000)
        
        mock_conn.recv.side_effect = [
            json.dumps({
                'type': 'move_request',
                'target': [10.0, 20.0]
            }).encode('utf-8'),
            json.dumps({
                'type': 'update',
                'position': [12.0, 22.0]
            }).encode('utf-8'),
            json.dumps({
                'type': 'reached'
            }).encode('utf-8'),
            b''
        ]
        
        handle_client(mock_conn, addr)
        
        self.assertNotIn(5000, players)
        self.assertNotIn(mock_conn, connections)
        mock_conn.close.assert_called_once()

    def test_concurrent_clients(self):
        # It tests handling multiple clients concurrently.
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        addr1 = ('127.0.0.1', 5001)
        addr2 = ('127.0.0.1', 5002)
        
        # Client 1 packets
        mock_conn1.recv.side_effect = [
            json.dumps({
                'type': 'move_request',
                'target': [10.0, 20.0]
            }).encode('utf-8'),
            b''
        ]
        
        # Client 2 packets
        mock_conn2.recv.side_effect = [
            json.dumps({
                'type': 'move_request',
                'target': [30.0, 40.0]
            }).encode('utf-8'),
            b''
        ]
        
        thread1 = threading.Thread(target=handle_client, args=(mock_conn1, addr1))
        thread2 = threading.Thread(target=handle_client, args=(mock_conn2, addr2))
        
        thread1.start()
        thread2.start()
        
        thread1.join(timeout=1)
        thread2.join(timeout=1)
        
        self.assertNotIn(5001, players)
        self.assertNotIn(5002, players)
        mock_conn1.close.assert_called_once()
        mock_conn2.close.assert_called_once()

if __name__ == '__main__':
    unittest.main(verbosity=2)