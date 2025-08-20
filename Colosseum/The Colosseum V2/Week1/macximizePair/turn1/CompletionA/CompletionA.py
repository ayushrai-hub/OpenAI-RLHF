def maximize_pair(a, b):
    a = list(str(a))
    b = list(str(b))
    n = len(a)
    
    # For each position
    for i in range(n):
        # If swapping would give us a larger product, do it
        if int(a[i]) < int(b[i]):
            a[i], b[i] = b[i], a[i]
    
    return ''.join(a), ''.join(b)

# Read number of test cases
t = int(input())

for _ in range(t):
    # Read a and b
    a = input().strip()
    b = input().strip()
    
    # Get maximized numbers
    max_a, max_b = maximize_pair(a, b)
    
    # Print results
    print(max_a)
    print(max_b)
