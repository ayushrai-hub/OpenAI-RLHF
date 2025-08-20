# Read input from stdin
n = int(input())

# Initialize an empty string
result = ''

# Concatenate numbers from 1 to n
for i in range(1, n + 1):
    result += str(i)

# Print the result
print(result)
