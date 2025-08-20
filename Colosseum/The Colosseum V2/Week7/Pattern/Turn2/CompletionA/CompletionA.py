rows = 4  # Total number of rows

for i in range(rows):
    # Print spaces before the pattern
    print(' ' * i, end='')
    
    # Calculate number of digits to print
    num_digits = 2 * (rows - i) - 1

    # Print the pattern of 1s and 0s
    for j in range(num_digits):
        if j % 2 == 0:
            print("1", end="")
        else:
            print("0", end="")
    
    # Move to the next line
    print()
