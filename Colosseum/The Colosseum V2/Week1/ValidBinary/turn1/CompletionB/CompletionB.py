def nthBinary(n):
    i = 2  # Start checking from 2 onwards.
    count = 0  # Counter for the number of qualifying binaries found.
    
    while True:
        b = bin(i)[2:]  # Convert the integer to binary string, removing the '0b' prefix.
        
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1  # Increment the count of valid binaries.
            if count == n:
                return b  # Return the nth valid binary number.
        
        i += 1  # Check the next integer.

# Printing the first 100 '1' '0' '1' sequences.
for i in range(1, 100):
    print(nthBinary(i))
