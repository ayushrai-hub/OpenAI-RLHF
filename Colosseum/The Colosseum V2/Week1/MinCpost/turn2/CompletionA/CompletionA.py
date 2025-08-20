def min_cost_to_make_good(s):
    count_zeros = s.count('0')
    count_ones = s.count('1')

    # The cost will be the largest of count_zeros or count_ones
    # because that's the minimum number of flips needed.
    return max(count_zeros, count_ones)