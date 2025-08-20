# ideal_completion.py

from itertools import permutations

def solve(l, w, d, length_costs, width_costs, depth_costs):
    MOD = 10**9 + 7
    total_instability = 0

    # Create a list of all cuts with their corresponding dimension
    cuts = [(length_costs[i], 'L') for i in range(l-1)] + \
           [(width_costs[i], 'W') for i in range(w-1)] + \
           [(depth_costs[i], 'D') for i in range(d-1)]
    
    # Initialize section counts for each dimension
    sections = {'L': 1, 'W': 1, 'D': 1}
    
    # For each permutation of cuts, calculate the instability
    for perm in permutations(cuts):
        # Reset section counts for each permutation
        sections = {'L': 1, 'W': 1, 'D': 1}
        instability = 0
        
        # Process each cut in the permutation order
        for factor, dim in perm:
            # Multiply the current cost by the number of sections in the other two dimensions
            other_dims = [sections[d] for d in 'LWD' if d != dim]
            instability += factor * other_dims[0] * other_dims[1]
            
            # Increment the section count for the current dimension
            sections[dim] += 1
        
        total_instability = (total_instability + instability) % MOD
    
    return total_instability