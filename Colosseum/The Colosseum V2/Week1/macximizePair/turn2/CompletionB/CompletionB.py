# Function to swap digits in a and b to maximize their product
def maximize_product(a, b):
    a = list(a)  # Convert a to a list of characters representing digits
    b = list(b)  # Convert b to a list of characters representing digits

    # Traverse both numbers and swap digits if needed to maximize the product
    for i in range(len(a)):
        # If swapping results in a better configuration for the product, swap
        if a[i] < b[i]:
            a[i], b[i] = b[i], a[i]

    # Return the modified versions of a and b as strings
    return ''.join(a), ''.join(b)

# Read the number of test scenarios
n = int(input())

# Iterate through each test scenario
for _ in range(n):
    # Read a and b as strings (since they can be very large numbers)
    a = input()
    b = input()
    
    # Maximize the product of a and b by swapping digits optimally
    max_a, max_b = maximize_product(a, b)
    
    # Print the optimized a and b
    print(max_a)
    print(max_b)
