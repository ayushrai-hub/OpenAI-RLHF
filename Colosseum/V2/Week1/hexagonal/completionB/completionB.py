def count_paths(n):
    # Create a 2D list (dp table) initialized to zero
    dp = [[0 for _ in range(n)] for _ in range(n)]
    
    # Start at the top-left corner
    dp[0][0] = 1
    
    # Fill the dp table
    for i in range(n):
        for j in range(n):
            # If moving to the bottom is within bounds
            if i + 1 < n:
                dp[i + 1][j] += dp[i][j]
                
            # If moving to the bottom-right is within bounds
            if i + 1 < n and j + 1 < n:
                dp[i + 1][j + 1] += dp[i][j]
                
            # If moving to the top-right is within bounds (top-right from next row up but still in bounds)
            if j + 1 < n:
                dp[i][j + 1] += dp[i][j]
    
    # The destination (bottom-right corner)
    return dp[n-1][n-1]

# Reading N from the input
n = int(input("Enter the side length of the hexagonal grid: "))

# Compute and display the number of paths
print("Number of ways to reach the opposite corner:", count_paths(n))
