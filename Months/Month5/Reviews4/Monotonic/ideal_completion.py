# ideal_completion.py
MOD = 10**9 + 7
def count_monotonic_pairs(nums):    
    n = len(nums)
    max_value = max(nums)
    dp = [[0]*(max_value+1) for _ in range(n+1)]
    dp[n] = [1]*(max_value+1)
    for i in range(n-1, -1, -1): 
        diff = 0 
        if i: diff = max(0, nums[i] - nums[i-1])
        for j in range(max_value, -1, -1): 
            if j+1 <= max_value: 
                dp[i][j] = dp[i][j+1]
            if j+diff <= nums[i]: 
                dp[i][j] = (dp[i][j] + dp[i+1][j+diff]) % MOD
    return dp[0][0]