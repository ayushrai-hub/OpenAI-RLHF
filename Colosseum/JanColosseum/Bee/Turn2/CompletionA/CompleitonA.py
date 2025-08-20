def hexagonal_grid_paths(n):
    # Initialize a 2D grid to store the number of paths to each cell.
    dp = [[0] * (2 * n - 1) for _ in range(2 * n - 1)]
    
    # The starting position (top-left corner) has one way to reach it.
    dp[0][0] = 1
    
    # Iterate over each possible cell in the grid.
    for r in range(2 * n - 1):
        for c in range(2 * n - 1):
            if dp[r][c] > 0:  # If there are paths to the current cell
                # Move to the cell directly below if within grid bounds
                if r + 1 < 2 * n - 1:
                    dp[r + 1][c] += dp[r][c]
                # Move to the bottom-right neighbor if within grid bounds
                if c + 1 < 2 * n - 1:
                    dp[r + 1][c + 1] += dp[r][c]
                # Move to the top-right neighbor if within grid bounds
                if r - 1 >= 0 and c + 1 < 2 * n - 1:
                    dp[r - 1][c + 1] += dp[r][c]
    
    # Sum up the paths that reach any cell in the last column
    result = sum(dp[r][2 * n - 2] for r in range(2 * n - 1))
    return result

# Input reading and output
N = int(input("Enter the side length of the hexagonal grid: "))
print(f"Number of ways for the bee to reach the opposite side: {hexagonal_grid_paths(N)}")
