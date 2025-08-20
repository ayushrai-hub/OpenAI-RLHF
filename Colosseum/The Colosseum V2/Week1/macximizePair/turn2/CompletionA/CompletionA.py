def maximize_product(a, b):
    a = list(str(a))
    b = list(str(b))
    
    for i in range(len(a)):
        if int(a[i]) < int(b[i]):
            a[i], b[i] = b[i], a[i]
    
    return int(''.join(a)), int(''.join(b))

# Read the number of test scenarios
n = int(input())

# Iterate through each test scenario
for _ in range(n):
    # Read a and b
    a = int(input())
    b = int(input())
    
    # Maximize the product of a and b
    max_a, max_b = maximize_product(a, b)
    
    # Print the maximized a and b
    print(max_a)
    print(max_b)
