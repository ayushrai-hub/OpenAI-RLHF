def calculate_bee_paths(N):
    # Create hexagonal grid representation
    grid_rows = [N + i for i in range(N)] + [2*N - i - 2 for i in range(N - 1)]
    total_rows = len(grid_rows)

    # Initialize DP array
    dp = [ [0]*row_len for row_len in grid_rows]
    dp[0][0] = 1  # Begin at top-left corner

    for r in range(total_rows):
        for c in range(grid_rows[r]):
            ways = dp[r][c]

            # Move Down
            if r + 1 < total_rows and c < grid_rows[r + 1]:
                dp[r + 1][c] += ways

            # Move Down-Right
            if r + 1 < total_rows and c + 1 < grid_rows[r + 1]:
                dp[r + 1][c + 1] += ways

            # Move Up-Right
            if r > 0 and c + 1 < grid_rows[r - 1]:
                dp[r - 1][c + 1] += ways

    # Endpoint is at the bottom-right corner
    return dp[-1][-1]

if __name__ == "__main__":
    N = int(input("Enter side length (N): "))
    ways = calculate_bee_paths(N)
    print(f"Number of ways the bee can reach the opposite corner: {ways}")
