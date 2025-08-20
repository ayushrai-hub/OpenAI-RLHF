rows = 4
for i in range(rows):
    # Print spaces
    print('  ' * i, end='')
    # Print pattern
    for j in range(2 * (rows - i) - 1):
        print('1' if j % 2 == 0 else '0', end='')
    print()
