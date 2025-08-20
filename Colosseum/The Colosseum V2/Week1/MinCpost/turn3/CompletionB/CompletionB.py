def min_cost_to_make_good(s):
    t = ''.join('1' if ch == '0' else '0' for ch in s)
    cost = sum(1 for i in range(len(s)) if s[i] != t[i])
    return cost

# Example usage:
s = "001"
print(min_cost_to_make_good(s))  # Output should be the number of changes needed
# test example
s = "001"
min_cost_to_make_good(s)  # Should be 2
