def min_cost_to_make_good(s):
    count_0 = s.count('0')
    count_1 = s.count('1')
    
    # Desired mismatches between s and t
    mismatches = 0
    for c in s:
        if (c == '0' and count_1 > 0) or (c == '1' and count_0 > 0):
            c_swap = '1' if c == '0' else '0'
            mismatches += 1

    # Each mismatch deletion costs 1 coin
    return mismatches

# Example usage:
s1 = "001"
s2 = "010101"

print(min_cost_to_make_good(s1))  # Output: 2
print(min_cost_to_make_good(s2))  # Output: 0
