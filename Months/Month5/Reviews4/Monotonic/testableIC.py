MOD = 10**9 + 7

def count_monotonic_pairs(nums):
    n = len(nums)
    max_val = max(nums)
    
    # Initialize dp array
    dp = [[0] * (max_val + 1) for _ in range(n + 1)]
    dp[0][0] = 1
    
    # Prefix sum to optimize sum calculations
    prefix_sum = [0] * (max_val + 1)
    
    for i in range(1, n + 1):
        prefix_sum[0] = dp[i-1][0]
        for j in range(1, max_val + 1):
            prefix_sum[j] = (prefix_sum[j-1] + dp[i-1][j]) % MOD
        
        for j in range(nums[i-1] + 1):
            dp[i][j] = prefix_sum[j] if j <= nums[i-1] else 0
    
    # Sum up all valid dp[n][j]
    result = sum(dp[n][j] for j in range(max_val + 1)) % MOD
    return result
