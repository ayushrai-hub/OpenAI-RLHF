def remove_values_no_greater_than_index(L):
    """
    Modifies the input list by removing elements not strictly greater than their index.
    """
    i = len(L) - 1
    while i >= 0:
        if L[i] <= i:
            L.pop(i)
        i -= 1

def cap_sum_to(n, L):
    """
    Returns a new list derived from L where the sum of elements does not exceed n.
    """
    new_list = sorted(L, reverse=True)
    result = []
    current_sum = 0
    for num in new_list:
        if current_sum + num <= n:
            result.append(num)
            current_sum += num
    return sorted(result)

def increasing_sequence_from(n, L):
    """
    Finds an increasing sequence in L starting from the leftmost occurrence of n.
    """
    if n not in L:
        return []
    
    result = []
    start_index = L.index(n)
    current = n
    
    for _ in range(len(L)):
        if L[start_index] >= current:
            result.append(L[start_index])           
            current = L[start_index] + 1
        start_index = (start_index + 1) % len(L)
    
    return result


# Example usage
if __name__ == "__main__":
    # Test remove_values_no_greater_than_index
    test_list1 = [3, 0, 5, 2, 4, 1]
    print("Original list:", test_list1)
    remove_values_no_greater_than_index(test_list1)
    print("After removing values no greater than index:", test_list1)

    # Test cap_sum_to
    test_list2 = [3, 1, 4, 1, 5, 9, 2, 6]
    cap = 10
    result = cap_sum_to(cap, test_list2)
    print(f"\nCapping sum to {cap}:", result)

    # Test increasing_sequence_from
    test_list3 = [3, 1, 4, 1, 5, 9, 2, 6]
    start = 1
    result = increasing_sequence_from(start, test_list3)
    print(f"\nIncreasing sequence starting from {start}:", result)