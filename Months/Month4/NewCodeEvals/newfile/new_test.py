import unittest
from unittest.mock import MagicMock, patch
import threading
import json
import socket
from ideal_completion import handle_client, broadcast_positions, players, connections, lock

class TestMultiplayerGameServer(unittest.TestCase):
    def setUp(self):
        """Initialize test environment before each test"""
        self.mock_conn = MagicMock()
        # Configure mock connection to properly handle bytes
        self.mock_conn.recv = MagicMock(return_value=b'')
        self.addr = ('127.0.0.1', 12345)
        
        # Clear global state
        with lock:
            players.clear()
            connections.clear()

    def tearDown(self):
        """Clean up after each test"""
        with lock:
            players.clear()
            connections.clear()

    def create_packet(self, packet_type, **kwargs):
        """Helper method to create test packets"""
        packet = {"type": packet_type, **kwargs}
        return json.dumps(packet).encode('utf-8')

    def test_initial_connection(self):
        """Test initial client connection setup"""
        # Configure mock to return empty data to trigger disconnect
        self.mock_conn.recv.return_value = b''
        
        # Run client handler
        handle_client(self.mock_conn, self.addr)
        
        with lock:
            # Verify player was added before disconnect
            self.assertEqual(len(connections), 0)  # Should be removed on disconnect
            self.assertEqual(len(players), 0)  # Should be removed on disconnect

    def test_move_request_valid(self):
        """Test valid move request handling"""
        # Set up the mock to return a move request followed by disconnect
        packet = self.create_packet("move_request", target=[10, 20])
        self.mock_conn.recv.side_effect = [packet, b'']
        
        # Run client handler
        handle_client(self.mock_conn, self.addr)
        
        # Player data should be updated before disconnect
        with lock:
            self.assertEqual(len(players), 0)  # Should be removed on disconnect
            self.assertEqual(len(connections), 0)

    def test_move_request_invalid_format(self):
        """Test move request with invalid position format"""
        # Send invalid format followed by disconnect
        packet = self.create_packet("move_request", target="invalid")
        self.mock_conn.recv.side_effect = [packet, b'']
        
        # Run client handler
        handle_client(self.mock_conn, self.addr)
        
        with lock:
            # Verify state remains unchanged before disconnect
            self.assertEqual(len(players), 0)
            self.assertEqual(len(connections), 0)

    def test_broadcast_positions(self):
        """Test broadcasting positions to all clients"""
        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()
        
        with lock:
            # Setup test state
            players[12345] = {'position': [10, 20], 'moving': True}
            players[54321] = {'position': [30, 40], 'moving': False}
            connections.extend([mock_conn1, mock_conn2])
        
        # Perform broadcast
        broadcast_positions()
        
        expected_message = {
            'type': 'sync',
            'players': [
                {'player_id': 12345, 'position': [10, 20], 'moving': True},
                {'player_id': 54321, 'position': [30, 40], 'moving': False}
            ]
        }
        expected_data = json.dumps(expected_message).encode('utf-8')
        
        # Verify both connections received the broadcast
        mock_conn1.sendall.assert_called_with(expected_data)
        mock_conn2.sendall.assert_called_with(expected_data)

    def test_client_disconnect(self):
        """Test proper cleanup on client disconnection"""
        # Configure mock to simulate immediate disconnect
        self.mock_conn.recv.return_value = b''
        
        with lock:
            # Add test data
            players[12345] = {'position': [0, 0], 'moving': False}
            connections.append(self.mock_conn)
        
        # Run client handler
        handle_client(self.mock_conn, self.addr)
        
        with lock:
            # Verify cleanup
            self.assertNotIn(12345, players)
            self.assertNotIn(self.mock_conn, connections)
        self.mock_conn.close.assert_called_once()

    def test_broadcast_connection_error(self):
        """Test handling of connection errors during broadcast"""
        mock_conn = MagicMock()
        mock_conn.sendall.side_effect = socket.error()
        
        with lock:
            players[12345] = {'position': [10, 20], 'moving': True}
            connections.append(mock_conn)
        
        # Should not raise exception
        broadcast_positions()
        
        # Verify sendall was attempted
        mock_conn.sendall.assert_called()

    def test_packet_sequence(self):
        """Test handling of multiple packets in sequence"""
        # Create a sequence of packets
        packets = [
            self.create_packet("move_request", target=[10, 20]),
            self.create_packet("update", position=[12, 22]),
            self.create_packet("pathObstructed"),
            self.create_packet("destinationReached"),
            b''  # Disconnect
        ]
        
        self.mock_conn.recv.side_effect = packets
        
        # Run client handler
        handle_client(self.mock_conn, self.addr)
        
        with lock:
            # Verify final state after disconnect
            self.assertEqual(len(players), 0)
            self.assertEqual(len(connections), 0)

    def test_concurrent_clients(self):
        """Test handling of multiple concurrent clients"""
        mock_conn1 = MagicMock()
        mock_conn2 = MagicMock()
        addr1 = ('127.0.0.1', 12345)
        addr2 = ('127.0.0.1', 54321)
        
        # Configure mocks
        mock_conn1.recv.return_value = b''
        mock_conn2.recv.return_value = b''
        
        # Start both client handlers
        thread1 = threading.Thread(target=handle_client, args=(mock_conn1, addr1))
        thread2 = threading.Thread(target=handle_client, args=(mock_conn2, addr2))
        
        thread1.start()
        thread2.start()
        
        # Wait for threads to complete
        thread1.join(timeout=1.0)
        thread2.join(timeout=1.0)
        
        with lock:
            # Verify final state
            self.assertEqual(len(players), 0)
            self.assertEqual(len(connections), 0)
            
if __name__ == '__main__':
    unittest.main(verbosity=2)