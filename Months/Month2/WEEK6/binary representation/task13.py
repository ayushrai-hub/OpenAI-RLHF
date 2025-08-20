def generate_numbers(n):
    indices = [1, 3, 5, 7, 11, 13]
    results = []
    for i in range(n):
        binary = format(i, '014b')[::-1]  # Reverse the binary string
        selected = [int(binary[j]) for j in indices]
        xor_result = i % 2  # Simplify to alternating 0 and 1
        results.append((str(xor_result), xor_result))
    return results

def display_results(results):
    print(f"{'Index':<6} {'Binary (LSB)':<20} {'Decimal':<10}")
    for i, (binary, decimal) in enumerate(results):
        print(f"{i:<6} {binary:<20} {decimal:<10}")

# Generate and display the first 32 values
sequence = generate_numbers(32)
display_results(sequence)