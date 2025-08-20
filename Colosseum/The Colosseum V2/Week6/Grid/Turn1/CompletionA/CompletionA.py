def bee_paths(N):
    # Maximum grid size calculation (rows and columns)
    grid_size = 2 * N - 1 
    dp = [[0] * grid_size for _ in range(grid_size)]
    
    # Starting point
    dp[0][0] = 1  

    for row in range(grid_size):
        for col in range(grid_size):
            # Skip cells outside the hexagonal shape
            if col - row >= N or row - col >= N:
                continue 
            # Possible movements
            # From upper cell (moving down)
            if row > 0:
                dp[row][col] += dp[row - 1][col]
            # From up-left cell (moving down-right)
            if row > 0 and col > 0:
                dp[row][col] += dp[row - 1][col - 1]
            # From lower-left cell (moving up-right)
            if col > 0 and row < grid_size - 1:
                dp[row][col] += dp[row + 1][col - 1]

    # Ending point (bottom-right)
    return dp[grid_size - 1][grid_size - 1]

# Reading input
N = int(input("Enter grid size N: "))
print("Number of ways:", bee_paths(N))
