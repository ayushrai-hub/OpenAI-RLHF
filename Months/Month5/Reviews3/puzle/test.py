import json
import unittest
import os
from testableIC import *

# Unit Test Class for verify_puzzle
class TestVerifyPuzzle(unittest.TestCase):
    def test_load_and_verify_valid_puzzle(self):
        """Test loading and verifying a valid puzzle from a file."""
        # Create a temporary JSON file with valid puzzle data
        temp_file_path = 'temp_puzzle.json'
        valid_puzzle_data = {
            "n": 3,
            "start": [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            "goal": [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        }
        
        # Write the valid puzzle data to the temporary file
        with open(temp_file_path, 'w') as file:
            json.dump(valid_puzzle_data, file)
        
        try:
            # Load the puzzle and verify it
            loaded_data = load_puzzle(temp_file_path)
            verify_puzzle(loaded_data)  # Should not raise an exception
        except Exception as e:
            self.fail(f"Test failed due to unexpected exception: {e}")
        finally:
            # Clean up: Remove the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Test 1: Missing required fields
    def test_missing_fields(self):
        """Test when one or more required fields are missing."""
        puzzle_data = {"n": 3, "start": [[1, 2, 3], [4, 5, 6], [7, 8, 0]]}  # Missing 'goal'
        with self.assertRaises(ValueError) as context:
            verify_puzzle(puzzle_data)

    # Test 2: Invalid n value (not an integer or less than or equal to 1)
    def test_invalid_n_value(self):
        """Test for invalid 'n' value (non-integer or <= 1)."""
        puzzle_data_1 = {"n": -2, "start": [[1, 0], [3, 2]], "goal": [[1, 2], [3, 0]]}  # 'n' is negative
        puzzle_data_2 = {"n": 1, "start": [[0]], "goal": [[0]]}  # 'n' is 1
        puzzle_data_3 = {"n": 2.5, "start": [[0]], "goal": [[0]]}  # 'n' is not an integer
        with self.assertRaises(ValueError):
            verify_puzzle(puzzle_data_1)
        with self.assertRaises(ValueError):
            verify_puzzle(puzzle_data_2)
        with self.assertRaises(ValueError):
            verify_puzzle(puzzle_data_3)

    # Test 3: Invalid matrix dimension for start/goal
    def test_invalid_matrix_dimension(self):
        """Test when 'start' or 'goal' matrices are not n x n."""
        puzzle_data = {
            "n": 3,
            "start": [[1, 2], [3, 4]],  # Not a 3x3 matrix
            "goal": [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        }
        with self.assertRaises(ValueError) as context:
            verify_puzzle(puzzle_data)

    # Test 4: Invalid numbers in matrices
    def test_invalid_matrix_numbers(self):
        """Test for invalid numbers in matrices (e.g., missing or duplicated numbers)."""
        puzzle_data = {
            "n": 3,
            "start": [[1, 2, 3], [4, 5, 6], [7, 8, 8]],  # Duplicated 8, missing 0
            "goal": [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
        }
        with self.assertRaises(ValueError) as context:
            verify_puzzle(puzzle_data)

    # Test 5: Valid puzzle data
    def test_valid_puzzle(self):
        """Test for a valid puzzle scenario."""
        puzzle_data = {
            "n": 3,
            "start": [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
            "goal": [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        }
        try:
            verify_puzzle(puzzle_data)
        except Exception:
            self.fail("verify_puzzle() raised Exception unexpectedly!")

    # Test 6: Larger puzzle (n = 4)
    def test_larger_puzzle(self):
        """Test a larger puzzle with n = 4."""
        puzzle_data = {
            "n": 4,
            "start": [
                [1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12],
                [13, 14, 15, 0]
            ],
            "goal": [
                [1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12],
                [13, 14, 15, 0]
            ]
        }
        try:
            verify_puzzle(puzzle_data)
        except Exception:
            self.fail("verify_puzzle() raised Exception unexpectedly!")


# Test Runner
if __name__ == '__main__':
    unittest.main(verbosity=2)
