def generate_numbers(first_n):
    # Define the sequence of indices to select from each binary representation
    indices = [1, 3, 5, 7, 11, 13]
    
    # Store results
    results = []

    for num in range(first_n):
        # Generate successive integers and convert them to binary
        binary_numbers = [format(i, 'b') for i in range(num + 1)]
        
        # Select numbers from the generated binary sequence based on specified indices
        selected_numbers = [int(binary_numbers[i], 2) for i in indices if i < len(binary_numbers)]
        
        # Compute the XOR of the selected numbers
        xor_result = 0
        for number in selected_numbers:
            xor_result ^= number

        # Convert the XOR result to binary and reverse it
        binary_result = format(xor_result, 'b')[::-1]
        
        # Append the result
        results.append((binary_result, xor_result))

    return results
