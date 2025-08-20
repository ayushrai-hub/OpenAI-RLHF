def min_cost_to_make_good(s):
    n = len(s)
    count_0 = s.count('0')
    count_1 = s.count('1')
    min_count = min(count_0, count_1)
    max_t_length = 2 * min_count
    total_deletions = n - max_t_length
    return total_deletions

# Examples
s1 = "001"
print(min_cost_to_make_good(s1))  # Output: 1

s2 = "0101"
print(min_cost_to_make_good(s2))  # Output: 0

s3 = "0000"
print(min_cost_to_make_good(s3))  # Output: 4 (needs to delete all characters to make it good)

s4 = "101010"
print(min_cost_to_make_good(s4))  # Output: 0
