import unittest
from itertools import permutations
from ideal_completion import solve

class TestTotalInstability(unittest.TestCase):
    
    def test_total_instability_basic(self):
        # Sample Input 0
        L = 2
        W = 2
        D = 2

        length_costs = [4] 
        width_costs = [1]         
        depth_costs = [2]     

        expected_output = 98
        
        result = solve(L, W, D, length_costs, width_costs, depth_costs)
        
        self.assertEqual(result, expected_output)

    
    def test_no_cuts(self):
        # Edge case with the smallest possible dimensions and no cuts
        L = 1  # No length cuts (L-1 = 0)
        W = 1  # No width cuts (W-1 = 0)
        D = 1  # No depth cuts (D-1 = 0)
        
        length_costs = []  # No cuts for length
        width_costs = []   # No cuts for width
        depth_costs = []   # No cuts for depth
        
        # Expected output should be 0 as no cuts are made, hence no instability
        expected_output = 0
        
        result = solve(L, W, D, length_costs, width_costs, depth_costs)
        
        self.assertEqual(result, expected_output)

    def test_total_instability_complex(self):
        
        L = 2 
        W = 2 
        D = 2 
        
        length_costs = [10]     
        width_costs = [5]               
        depth_costs = [25]    

        # Expected output calculated manually using the explanation provided by user
        expected_output = 560
        
        result = solve(L, W, D, length_costs, width_costs, depth_costs)
        
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main(verbosity=2)