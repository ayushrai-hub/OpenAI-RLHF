def hexagonal_grid_paths(N):
    # Total rows in the hexagonal grid
    total_rows = 2 * N - 1
    
    # Represent the hexagonal grid as 2-D DP array
    dp = []
    for r in range(total_rows):
        row_length = N + r if r < N else 3 * N - 2 - r
        dp.append([0] * row_length)
    
    # Initialize the starting position (top-left corner)
    dp[0][0] = 1
    
    # Fill the DP table
    for r in range(total_rows):
        for c in range(len(dp[r])):
            if dp[r][c] > 0:  # If there's a way to reach this cell
                if r + 1 < total_rows:
                    if c < len(dp[r + 1]):  # Move "down"
                        dp[r + 1][c] += dp[r][c]
                    if c + 1 < len(dp[r + 1]):  # Move "bottom-right"
                        dp[r + 1][c + 1] += dp[r][c]
                if r - 1 >= 0 and c + 1 < len(dp[r - 1]):  # Move "top-right"
                    dp[r - 1][c + 1] += dp[r][c]

    # The bottom-right corner is the last cell in the last row
    return dp[-1][-1]

# Input
N = int(input("Enter the side length of the hexagonal grid (N): "))
print("Number of ways for the bee to reach the opposite corner:", hexagonal_grid_paths(N))
