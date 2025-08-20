# Read integer input
n = int(input().strip())

# Initialize an empty string to accumulate the sequence
result = ''

# Loop through 1 to n and build the concatenated string
for i in range(1, n + 1):
    result += str(i)

# Print the resulting string
print(result)
