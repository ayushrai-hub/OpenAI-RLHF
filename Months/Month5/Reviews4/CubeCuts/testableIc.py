MOD = 10**9 + 7

def modinv(a, mod):
    return pow(a, mod - 2, mod)

def preprocess_factorials(max_n, mod):
    factorials = [1] * (max_n + 1)
    inv_factorials = [1] * (max_n + 1)
    for i in range(2, max_n + 1):
        factorials[i] = factorials[i - 1] * i % mod
    inv_factorials[max_n] = modinv(factorials[max_n], mod)
    for i in range(max_n - 1, 0, -1):
        inv_factorials[i] = inv_factorials[i + 1] * (i + 1) % mod
    return factorials, inv_factorials

def solve(l, w, d, length_costs, width_costs, depth_costs):
    n = l + w + d - 3  # Total number of cuts
    factorials, inv_factorials = preprocess_factorials(n, MOD)
    
    def sum_contributions(costs, total_segments):
        m = len(costs)
        result = 0
        for i, cost in enumerate(costs):
            segments_cut = (i + 1)
            remaining_segments = total_segments - segments_cut
            contrib = cost * factorials[n] % MOD
            contrib = contrib * inv_factorials[segments_cut - 1] % MOD
            contrib = contrib * inv_factorials[remaining_segments] % MOD
            result = (result + contrib) % MOD
        return result
    
    total_segments = 1
    total_instability = 0
    
    # Length contributions
    total_instability = (total_instability + sum_contributions(length_costs, l)) % MOD
    
    # Width contributions
    total_instability = (total_instability + sum_contributions(width_costs, w)) % MOD
    
    # Depth contributions
    total_instability = (total_instability + sum_contributions(depth_costs, d)) % MOD
    
    return total_instability
