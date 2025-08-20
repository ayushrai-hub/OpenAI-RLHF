def hex_grid_paths(n):
    """
    Calculate the number of ways a bee can move from top-left (0,0) to 
    bottom-right (n-1, n-1) in a hexagonal grid with n cells per side.
    Assumes moves: right, down-right, down-left (hexagonal coordinates).
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    
    # Create a DP table for coordinates (i,j)
    # In hex grid, we'll use a triangular shape where i + j < n
    dp = [[0] * n for _ in range(n)]
    
    # Base case: starting position (0,0) has 1 way
    dp[0][0] = 1
    
    # Fill the DP table
    for i in range(n):
        for j in range(n):
            if i + j >= n:  # Beyond the triangular grid boundary
                continue
            # Add paths from possible previous positions
            # In hex grid: up-left, up-right, left moves (reverse to reach (i,j))
            if i > 0:  # From up
                dp[i][j] += dp[i-1][j]
            if j > 0:  # From left
                dp[i][j] += dp[i][j-1]
            if i > 0 and j < n-1:  # From up-right
                dp[i][j] += dp[i-1][j+1]
    
    # The destination is (n-1, 0) in this triangular arrangement
    return dp[n-1][0]

# Main program
def main():
    # Get input from user
    try:
        n = int(input("Enter the size of the hexagonal grid (N): "))
        if n < 1:
            print("Please enter a positive integer.")
            return
        
        # Calculate and display the result
        result = hex_grid_paths(n)
        print(f"Number of ways for the bee to reach the opposite corner: {result}")
        
    except ValueError:
        print("Please enter a valid integer.")

if __name__ == "__main__":
    main()
