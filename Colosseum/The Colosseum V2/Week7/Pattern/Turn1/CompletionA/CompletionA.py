n = 4  # Number of lines

for i in range(n):
    # Print spaces before the pattern
    print(' ' * i, end='')
    # Print pattern of alternating 1s and 0s
    for j in range(2 * (n - i) - 1):
        print(j % 2, end="")
    print()
