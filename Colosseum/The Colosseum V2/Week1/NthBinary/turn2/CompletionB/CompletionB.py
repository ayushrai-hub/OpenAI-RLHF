def nthBinary(n):
    i = 2
    count = 0
    while True:
        b = bin(i)[2:]  # Convert integer to binary string and remove '0b' prefix
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1
            if count == n:
                return b
        i += 1

# Adjusting for the pattern '1' '0' * n + '1'
for n in range(1, 100):
    s = ''
    s += '1'  # Start with '1'
    s += '0' * n  # Followed by '0's repeated 'n' times
    s += '1'  # End with '1'
    print(f"n = {n}: {s}")
