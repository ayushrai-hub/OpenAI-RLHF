def count_paths(N):
    # Initialize a DP table with dimensions (2N-1, N) where dp[y][x] represents
    # the number of ways to reach that cell (y, x) from the left-top (0, 0)
    dp = [[0 for _ in range(N)] for _ in range(2 * N - 1)]
    
    # Start at top left corner
    dp[0][0] = 1

    # Fill the DP table
    for y in range(2 * N - 1):
        for x in range(N):
            if dp[y][x] > 0:
                if y + 1 < 2 * N - 1:  # Can move down
                    dp[y + 1][x] += dp[y][x]
                if x + 1 < N:  # Can move down-right
                    dp[y][x + 1] += dp[y][x]
                if y - 1 >= 0 and x + 1 < N:  # Can move top-right
                    dp[y - 1][x + 1] += dp[y][x]

    # The bottom-right corner of the grid is at dp[N-1][N-1]
    return dp[N-1][N-1]

# Main function to read input N and calculate result
def main():
    N = int(input("Enter the side length N of the hexagonal grid: "))
    result = count_paths(N)
    print(f"The number of ways the bee can move to the opposite corner is: {result}")

if __name__ == "__main__":
    main()
