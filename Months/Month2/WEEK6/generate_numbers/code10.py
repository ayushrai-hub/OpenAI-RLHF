def generate_numbers(first_n):
    results = []
    for num in range(first_n):
        # For odd numbers, the result is 1; for even numbers, it's 0
        binary_result = '1' if num % 2 else '0'
        decimal_result = 1 if num % 2 else 0
        results.append((binary_result, decimal_result))
    
    # Print the results in a formatted table
    print(f"{'Index':<6} {'Binary (LSB)':<12} {'Decimal':<10}")
    for i, (binary_result, decimal_result) in enumerate(results):
        print(f"{i:<6} {binary_result:<12} {decimal_result:<10}")
    
    return results  