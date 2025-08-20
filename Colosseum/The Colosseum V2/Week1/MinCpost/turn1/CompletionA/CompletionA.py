def min_cost_to_make_good(s):
    n0 = s.count('0')  # Count '0's in the string s
    n1 = len(s) - n0  # Count '1's in the string s (since all characters are 0 or 1)
    
    m0 = n1  # Ideal cases in t: n1 '0's and n0 '1's for optimal arrangement
    m1 = n0

    deletions_for_0 = abs(n0 - m0)  # Count for deleting excess '0's or adding deficient '0's
    deletions_for_1 = abs(n1 - m1)  # Count for deleting excess '1's or adding deficient '1's

    # Total cost for deletions
    total_cost = deletions_for_0 + deletions_for_1
    return total_cost

# Example usage:
s = "001"
print(min_cost_to_make_good(s))  # Should return the minimum cost to transform it
