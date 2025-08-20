# ideal_completion.py
import json

def load_puzzle(file_path):
    # Open the JSON file and load the data
    with open(file_path, 'r') as file:
        puzzle_data = json.load(file)
    
    # Return the parsed data
    return puzzle_data

def verify_puzzle(puzzle_data):
    # Check if the required fields are present
    required_fields = ['n', 'start', 'goal']
    for field in required_fields:
        if field not in puzzle_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Check if 'n' is a positive integer greater than 1
    n = puzzle_data['n']
    if not isinstance(n, int) or n <= 1:
        raise ValueError("'n' must be a positive integer greater than 1")
    
    # Verify if 'start' and 'goal' are n x n matrices with valid numbers
    def is_valid_matrix(matrix, size):
        return (
            isinstance(matrix, list) and
            len(matrix) == size and
            all(isinstance(row, list) and len(row) == size for row in matrix) and
            set(item for row in matrix for item in row) == set(range(size * size))
        )

    if not is_valid_matrix(puzzle_data['start'], n):
        raise ValueError(f"'start' must be an {n}x{n} matrix with numbers from 0 to {n*n-1}")

    if not is_valid_matrix(puzzle_data['goal'], n):
        raise ValueError(f"'goal' must be an {n}x{n} matrix with numbers from 0 to {n*n-1}")

    print("The puzzle input is valid.")

def main():
    try:
        # Load puzzle from a given JSON file path
        puzzle_data = load_puzzle('puzzle.json')
        
        # Verify loaded puzzle data
        verify_puzzle(puzzle_data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
