import unittest
from unittest.mock import patch
import time

from testableIC import (
    compress_pub_key,
    public_key_to_address,
    quantum_superposition_search,
    process_batch,
    alien_search_for_key,
    G,
    N
)

class TestBitcoinKeySearch(unittest.TestCase):
    def setUp(self):
        # It sets up test fixtures.
        self.known_private_key = 12345
        self.known_pub_point = self.known_private_key * G
        self.known_compressed_pubkey = compress_pub_key(
            self.known_pub_point.x, 
            self.known_pub_point.y
        )
        self.known_address = public_key_to_address(self.known_compressed_pubkey)

    def test_compress_pub_key(self):
        # It tests the public key compression.
        # Test even y coordinate
        even_y_point = G  # Generator point
        compressed = compress_pub_key(even_y_point.x, even_y_point.y)
        self.assertTrue(compressed.startswith('02') or compressed.startswith('03'))
        self.assertEqual(len(compressed), 66)  # 33 bytes in hex = 66 chars

        # Test odd y coordinate
        odd_y_point = 2 * G
        compressed = compress_pub_key(odd_y_point.x, odd_y_point.y)
        self.assertTrue(compressed.startswith('02') or compressed.startswith('03'))
        self.assertEqual(len(compressed), 66)

    def test_public_key_to_address(self):
        # It tests the Bitcoin address generation.
        # Test with known public key
        address = public_key_to_address(self.known_compressed_pubkey)
        self.assertTrue(isinstance(address, str))
        self.assertTrue(address.startswith('1'))  # Mainnet address
        
        # Test address format using correct base58 alphabet
        BASE58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        address_bytes = address.encode('ascii')
        self.assertTrue(all(b in BASE58_ALPHABET for b in address_bytes))
        
        # Test address length
        self.assertGreaterEqual(len(address), 26)
        self.assertLessEqual(len(address), 35)

    def test_quantum_superposition_search(self):
        # It tests quantum-inspired random number generation.
        start = 1
        end = 1000
        attempts = 50
        
        # Test range and count
        results = quantum_superposition_search(start, end, attempts)
        self.assertEqual(len(results), attempts)
        self.assertTrue(all(start <= x <= end for x in results))
        
        # Test randomness (basic check)
        another_results = quantum_superposition_search(start, end, attempts)
        self.assertNotEqual(results, another_results)  # Very unlikely to be equal

    def test_process_batch(self):
        # It tests batch processing of private keys.
        # Test with known private key in batch
        test_batch = [self.known_private_key, self.known_private_key + 1]
        result = process_batch(
            test_batch,
            self.known_compressed_pubkey,
            self.known_address
        )
        self.assertEqual(result, self.known_private_key)
        
        # Test with no match
        wrong_batch = [self.known_private_key + 1, self.known_private_key + 2]
        result = process_batch(
            wrong_batch,
            self.known_compressed_pubkey,
            self.known_address
        )
        self.assertIsNone(result)

    def test_alien_search_for_key(self):
        # It tests the main search function.
        # Test successful search scenario
        with patch('time.time', autospec=True) as mock_time:
            # Create a counter for the time mock
            time_counter = 0
            def time_side_effect():
                nonlocal time_counter
                time_counter += 30
                return time_counter
            mock_time.side_effect = time_side_effect
            
            with patch('random.randint', return_value=self.known_private_key):
                result = alien_search_for_key(
                    self.known_compressed_pubkey,
                    self.known_address,
                    max_attempts=100,
                    batch_size=10,
                    time_limit=60
                )
                self.assertEqual(result, self.known_private_key)
        
        # Test timeout scenario
        with patch('time.time', autospec=True) as mock_time:
            mock_time.return_value = 301  # Constant time beyond limit
            
            result = alien_search_for_key(
                self.known_compressed_pubkey,
                self.known_address,
                max_attempts=100,
                batch_size=10,
                time_limit=300
            )
            self.assertIsNone(result)

    def test_input_validation(self):
        # It tests input validation and edge cases.
        # Test invalid public key format
        with self.assertRaises(ValueError):
            public_key_to_address("invalid_key")
        
        # Test quantum search with invalid range
        with self.assertRaises(ValueError):
            quantum_superposition_search(100, 1, 10)  # end < start
        
        # Test process_batch with empty batch
        result = process_batch([], self.known_compressed_pubkey, self.known_address)
        self.assertIsNone(result)

    @patch('time.sleep')  # Add sleep patch to prevent actual waiting
    def test_performance_limits(self, mock_sleep):
       # It tests performance and resource limits.
        # Use smaller batch size for testing
        test_batch_size = 100
        
        start_time = time.time()
        
        # Test batch processing speed with smaller batch
        large_batch = quantum_superposition_search(1, 1000, test_batch_size)  # Reduced range
        result = process_batch(
            large_batch,
            self.known_compressed_pubkey,
            self.known_address
        )
        
        processing_time = time.time() - start_time
        self.assertLess(processing_time, 5.0)  # Should process within 5 seconds
        
        # Test memory usage (basic check)
        import sys
        batch_size_bytes = sys.getsizeof(large_batch)
        self.assertLess(batch_size_bytes, 1024 * 1024)  # Should be less than 1MB

if __name__ == '__main__':
    unittest.main(verbosity=2)