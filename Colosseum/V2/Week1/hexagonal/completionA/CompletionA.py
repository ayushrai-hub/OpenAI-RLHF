def count_ways(n):
    # Using dynamic programming to count paths
    # dp[i][j] represents the number of ways to reach cell (i, j)
    dp = [[0 for _ in range(n)] for _ in range(2*n-1)]

    # Starting position
    dp[0][0] = 1

    # Fill the DP table
    for i in range(2*n-1):
        for j in range(min(i, n-1)+1):
            if dp[i][j] > 0:
                # Move bottom
                if i + 1 < 2*n-1:
                    dp[i+1][j] += dp[i][j]
                # Move bottom-right
                if j + 1 < n and i + 1 < 2*n-1:
                    dp[i+1][j+1] += dp[i][j]
                # Move top-right
                if j + 1 < n and i - 1 >= 0:
                    dp[i-1][j+1] += dp[i][j]

    return dp[2*n-2][n-1]

# Input N
N = int(input("Enter N: "))
print("Number of ways to reach the opposite side:", count_ways(N))
