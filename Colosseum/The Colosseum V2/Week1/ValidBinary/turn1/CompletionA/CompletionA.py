def nthBinary(n):
    i = 2  
    count = 0  
    while True:
        b = bin(i)[2:]  
        
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1
            if count == n:
                return b  
        i += 1

# Generate and print the first 100 valid binary strings as per the problem
for i in range(1, 100):
    print(nthBinary(i))
