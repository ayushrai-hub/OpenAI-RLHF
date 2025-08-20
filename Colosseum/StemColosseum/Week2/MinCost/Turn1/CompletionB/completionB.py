def min_cost_to_make_good(s):
    n = len(s)
    i = 0
    cost = 0

    while i < n - 1:
        # Check for adjacent pairs of different characters
        if s[i] != s[i + 1]:
            # We can remove both characters of this pair
            cost += 1
            i += 2  # Skip the next character since we removed it as a pair
        else:
            # Move to the next character if they are the same
            i += 1

    # After processing, if there is anything left (like an unmatched last character), we'll have to remove it
    if i < n:
        cost += 1

    return cost

# Test cases
print(min_cost_to_make_good("001"))  # Output should be 1
print(min_cost_to_make_good("0110"))  # Output should be 0
print(min_cost_to_make_good("010101"))  # Output should be 0
