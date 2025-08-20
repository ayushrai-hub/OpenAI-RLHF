# Read the input integer n
n = int(input())

# Generate the sequence as a string
result = ''.join(str(i) for i in range(1, n+1))

# Output the result
print(result)
