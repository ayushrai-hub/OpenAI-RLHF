def count_paths_hex(N):
    # Number of cells in each direction for a hexagonal domain
    matrix_size = 2*N - 1

    # Initialize the grid
    layer = [[0] * matrix_size for _ in range(matrix_size)]
    grid = [layer * matrix_size for _ in range(matrix_size)]

    # Initialize the expansion queue
    expansion_queue = [(-(N-1), 0, (N-1))]
    while len(expansion_queue):
        # Cube coordinates
        q, r, s = expansion_queue.pop()
        # Index in the grid
        i, j, k = (q + matrix_size//2, r + matrix_size//2, s + matrix_size//2)
        grid[i][j][k] += 1

        # Which cells can be reached using the allowed moves
        connected_cells = {
            "down": (q, r+1, s-1),
            "up-right": (q+1, r-1, s),
            "down-right": (q+1, r, s-1)
        }

        # Are the allowed moves admissible?
        for dir in connected_cells:
            if abs(connected_cells[dir][0]) < N and \
                  abs(connected_cells[dir][1]) < N and \
                  abs(connected_cells[dir][2]) < N:
                expansion_queue.append(connected_cells[dir]) 
    
    bottom_right = ((N-1, 0, -(N-1)))
    return grid[bottom_right[0]+matrix_size//2][bottom_right[1]+matrix_size//2][bottom_right[2]+matrix_size//2]

# Read input from the user
N = int(input("Enter the side length of the hexagonal grid (N): "))
print(f"Number of paths in hexagonal {N}x{N}x{N} domain:", count_paths_hex(N))
