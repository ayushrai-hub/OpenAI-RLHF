# Program to print the pattern

# First row has 7 characters
# Each row reduces by 2 characters
# Spaces increase by 2 in each row

def print_pattern():
    pattern = "1010101"
    spaces = 0
    
    for i in range(4):  # We need 4 rows
        # Print spaces first
        print(" " * spaces, end="")
        # Print the pattern
        print(pattern)
        
        # Reduce pattern by removing first and last character
        pattern = pattern[1:-1]
        # Increase spaces by 2 for next row
        spaces += 2

# Call the function
print_pattern()

print(" \n Second code snippet \n")
# Simpler version using just one loop

rows = 4
pattern = "1010101"

for i in range(rows):
    print(" " * (i*2) + pattern[i:7-i])
