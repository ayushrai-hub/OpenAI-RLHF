def nthBinary(n):
    i = 2  # start checking from 2 upwards
    count = 0  # valid count
    
    while True:
        b = bin(i)[2:]  # get binary representation of i without '0b'
        
        # Check the conditions:
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1
            if count == n:
                return b  # this is the nth valid binary number
        
        i += 1  # go to the next number

# Generate and print the first 100 '1' '0' *n + '1' sequences
for i in range(1, 101):
    print(nthBinary(i))
