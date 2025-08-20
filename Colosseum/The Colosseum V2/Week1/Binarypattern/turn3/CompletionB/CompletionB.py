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

def smallestBinary(n):
    return '1' + '0' * n + '1'

# Generate the list of binary numbers from nthBinary
nth_binaries = [nthBinary(i) for i in range(1, 100)]

# Start with the smallest binary and swap
n = 1
while True:
    smallest = smallestBinary(n)
    if smallest not in nth_binaries:
        break
    
    index = nth_binaries.index(smallest)
    print(f"Swapping {smallest} with {nth_binaries[index]} (n={n})")
    
    # Perform the swap
    nth_binaries[index] = smallest
    
    n += 1

print("\nFinal list after swaps:")
for i, b in enumerate(nth_binaries, 1):
    print(f"{i}: {b}")
