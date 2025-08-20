def nthBinary(n):
    i = 2
    count = 0
    while True:
        b = bin(i)[2:]  # Get binary representation, discarding the '0b' prefix
        if b[0] == '1' and '01' not in b and b[-1] == '0':
            # Binary sequence should start with '1', contain no '01', and end in '0'
            count += 1
            if count == n:  # Return nth binary fitting the criteria
                return b
        i += 1


def generate_pattern(n):
    # This produces the input string '1' + ('0' * n) + '1'
    return '1' + ('0' * n) + '1'


def swap_with_nth_binary(start_str, nth_binary):
    # Swap each character from start_str with nth_binary if possible
    min_len = min(len(start_str), len(nth_binary))
    # Generate the swapped string
    swapped = ''.join(nth_binary[i] if i < len(nth_binary) else '' for i in range(min_len))
    return swapped


# Example: Let's try swapping up to n = 10

for n in range(1, 11):
    start_str = generate_pattern(n)
    nth_bin = nthBinary(n)
    swapped_str = swap_with_nth_binary(start_str, nth_bin)
    print(f"n = {n}, start_str = {start_str}, nth_binary = {nth_bin}, swapped = {swapped_str}")
