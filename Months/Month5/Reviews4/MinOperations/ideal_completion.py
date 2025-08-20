# ideal_completion.py
# Initialize memory and prefix arrays
mem = [0] * (int(2e5) + 1)
prefix = [0] * (int(2e5) + 1)

def update_mem(i):
    # Base cases for recursion
    if i < 3:
        mem[i] = 1
        return 1
    if mem[i] != 0:
        return mem[i]
    # Recursive case
    mem[i] = 1 + update_mem(i // 3)
    return mem[i]

# Populate the mem and prefix arrays
for i in range(int(2e5) + 1):
    update_mem(i)
    if i == 0:
        prefix[i] = 1
    else:
        prefix[i] = prefix[i - 1] + mem[i]

def min_operations_to_zero(t, test_cases):
    results = []
    for l, r in test_cases:
        results.append(prefix[r] - prefix[l - 1] + mem[l])
    return results

if __name__=="__main__":
    t = int(input())
    test_cases = []
    for _ in range(t):
        l,r = map(int, input().split())
        test_cases.append((l,r))
    results = min_operations_to_zero(t, test_cases)
    for r in results:
        print(r)