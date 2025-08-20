def nthBinary(n):
    i = 2  # Start from binary number 2 ('10')
    count = 0  # To count valid binary numbers
    while True:
        b = bin(i)[2:]  # Get the binary representation of the number without the '0b' prefix
        
        # Check the specific conditions: first is '1', doesn't contain '01', and ends with '0'
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            count += 1  # Increment count for valid binary numbers
            if count == n:
                return b  # Return the nth valid binary number
        i += 1  # Go to the next number

# Generate and print the first 99 such binary numbers
for i in range(1, 100):
    print(nthBinary(i))

# Generate the initial string and swap characters with the nth binary numbers generated
n = 2 # You can change n to any integer value you prefer

initial_string = '1' + '0' * n + '1'

print("Initial string:", initial_string)

swapped_strings = []
for i in range(1, 100):
    nth_bin = nthBinary(i)
    min_len = min(len(initial_string), len(nth_bin))
    
    swapped = ''.join(nth_bin[j] if j < len(nth_bin) else initial_string[j]
                      for j in range(min_len))
    
    # Append the remaining characters if any string is longer
    if len(initial_string) > min_len:
        swapped += initial_string[min_len:]
    elif len(nth_bin) > min_len:
        swapped += nth_bin[min_len:]
    
    swapped_strings.append(swapped)

# Print the result of swapping
for i, s in enumerate(swapped_strings, start=1):
    print(f"Swapped string {i}: {s}")
