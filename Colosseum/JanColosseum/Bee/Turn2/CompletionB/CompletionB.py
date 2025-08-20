def count_paths(N):
    # The value of grid[i][j] represents the number of valid paths that can
    # reach that cell. The top cell on the left side of the grid
    # is the origin (0, 0); the bottom right cell is at (N-1, N-1).

    # Initialize the hexagonal grid
    grid = [[0] * N for _ in range(N)]

    # Initialize the expansion queue
    expansion_queue = [(0,0)]
    while len(expansion_queue):
        # Offset coordinates are equivalent to grid index
        row, col = expansion_queue.pop()
        grid[row][col] += 1

        # Which cells can be reached using the allowed moves
        connected_cells = {
            "down": (row + 1, col),
            "up-right": (row - 1 if (col % 2 == 0) else row, col + 1),
            "down-right": (row + 1 if (col % 2 == 1) else row, col + 1)
        }

        # Are the allowed moves admissible?
        for direction in connected_cells:
            # Domain is strictly positive
            if connected_cells[direction][0] < 0 or connected_cells[direction][1] < 0:
                continue
            
            # There are N cells per side; all indices must be strictly less than N
            if connected_cells[direction][0] < N and connected_cells[direction][1] < N:
                expansion_queue.append(connected_cells[direction])
    
    return grid[-1][-1]

# Read input from the user
N = int(input("Enter the side length of the hexagonal grid (N): "))
print("Number of paths:", count_paths(N))
