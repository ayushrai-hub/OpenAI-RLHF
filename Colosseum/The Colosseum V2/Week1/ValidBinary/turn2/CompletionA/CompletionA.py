def nthBinary(n):
    i = 2  # start checking from the first number after '1'
    count = 0  # to count how many valid binary numbers we've found
    while True:
        b = bin(i)[2:]  # Convert the number to binary string
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1  # Increment valid binary count
            if count == n:
                return b  # Return the nth valid binary sequence
        i += 1  # Move to the next number

# Print out the first 100 '1' '0' '1' binary sequences
for i in range(1, 101):
    print(nthBinary(i))
