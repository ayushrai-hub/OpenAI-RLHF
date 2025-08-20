# Define allowed moves in axial coordinates
# Moves: down, down-right, up-right
moves = [(0, 1), (1, 0), (1, -1)]

def is_valid(q, r, N):
    # Checks if (q, r) is within hexagon grid boundaries
    return (0 <= q <= 2 * N - 2 and
            max(0, q - N + 1) <= r <= min(q, N - 1))

def count_paths(N):
    # DP dictionary to store number of ways to reach cell (q, r)
    dp = {}

    # start position
    dp[(0, 0)] = 1

    # Iterate over possible q and r in range
    for q in range(0, 2 * N - 1):
        for r in range(max(0, q - N + 1), min(q, N - 1) + 1):
            curr = dp.get((q, r), 0)
            for dq, dr in moves:
                nq, nr = q + dq, r + dr
                if is_valid(nq, nr, N):
                    dp[(nq, nr)] = dp.get((nq, nr), 0) + curr

    # Target (bottom-right) at (2N - 2, N - 1)
    return dp.get((2 * N - 2, N - 1), 0)

# Read N from input
N = int(input("Enter N: "))

# Compute number of ways
ways = count_paths(N)

print(f"Number of ways: {ways}")
