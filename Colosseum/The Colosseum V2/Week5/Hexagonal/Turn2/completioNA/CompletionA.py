def count_bee_paths(N):
    # Create a 2D grid to store the number of paths
    # The grid needs to be (2N-1) x (2N-1) to accommodate all possible positions
    dp = [[0] * (2*N-1) for _ in range(2*N-1)]
    
    # Starting position (top-left) has 1 path
    dp[0][0] = 1
    
    # For each row
    for i in range(2*N-1):
        # For each column
        for j in range(2*N-1):
            # Skip if we're outside the hexagonal grid
            if abs(i - j) >= N:
                continue
            
            # If we're not in the first position, calculate paths
            if i > 0 or j > 0:
                # Add paths from above (down movement)
                if i > 0:
                    dp[i][j] += dp[i-1][j]
                
                # Add paths from left (down-right movement)
                if j > 0:
                    dp[i][j] += dp[i][j-1]
                
                # Add paths from below-left (up-right movement)
                if i > 0 and j > 0:
                    dp[i][j] += dp[i-1][j-1]
    
    # Return the value at the bottom-right corner
    return dp[N-1][N-1]

# Read input
N = int(input())

# Calculate and print result
result = count_bee_paths(N)
print(result)
