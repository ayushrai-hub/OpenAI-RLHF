def maximize_product(a, b):
    # Convert a and b from strings to lists of digits
    a_digits = list(a)
    b_digits = list(b)
    
    # Sort digits of both lists in descending order
    a_digits.sort(reverse=True)
    b_digits.sort(reverse=True)
    
    # Reassemble the sorted lists back into strings
    a_maximized = ''.join(a_digits)
    b_maximized = ''.join(b_digits)
    
    return a_maximized, b_maximized

# Read the number of test scenarios
n = int(input().strip())

# Iterate through each test scenario
for _ in range(n):
    # Read the integers as strings
    a = input().strip()
    b = input().strip()
    
    # Maximize the product of a and b by swapping digits
    max_a, max_b = maximize_product(a, b)
    
    # Print the results
    print(max_a)
    print(max_b)
