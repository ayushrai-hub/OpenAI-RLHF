def min_operations_to_zero(t, test_cases):
    results = []
    for l, r in test_cases:
        results.append(r - l + 1)
    return results

if __name__ == "__main__":
    # Reading input
    import sys
    input = sys.stdin.read
    data = input().split()

    t = int(data[0])
    test_cases = []
    index = 1
    for _ in range(t):
        l = int(data[index])
        r = int(data[index + 1])
        test_cases.append((l, r))
        index += 2

    # Compute results
    results = min_operations_to_zero(t, test_cases)

    # Output results
    for result in results:
        print(result)
