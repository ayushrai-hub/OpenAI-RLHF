import unittest
from ideal_completion import optimal_bipartite_matching

class TestOptimalBipartiteMatching(unittest.TestCase):

    def setUp(self):
        self.points_x = [(1, 2), (3, 4), (5, 0), (2, 3), (6, 7)]
        self.points_y = [(2, 1), (4, 3), (0, 5), (3, 2), (7, 6)]
    
    def test_optimal_bipartite_matching_basic(self):
        # Test if the function returns a list of matches and a numeric total cost
        matches, total_cost = optimal_bipartite_matching(self.points_x, self.points_y)
        self.assertIsInstance(matches, list)
        self.assertIsInstance(total_cost, (float, int))
        
    def test_optimal_bipartite_matching_correct_matches(self):
        # Test if each match is within the range of points_x and points_y indices
        matches, _ = optimal_bipartite_matching(self.points_x, self.points_y)
        for match in matches:
            row, col = match
            self.assertIn(row, range(len(self.points_x)))
            self.assertIn(col, range(len(self.points_y)))      

    def test_optimal_bipartite_matching_expected_return(self):
        # Test if the function returns the expected matches and total cost
        expected_matches = [(0, 0), (1, 1), (2, 3), (3, 2), (4, 4)]
        expected_total_cost = 9.899494936611667
        matches, total_cost = optimal_bipartite_matching(self.points_x, self.points_y)
        self.assertEqual(matches, expected_matches)
        self.assertEqual(total_cost, expected_total_cost)

if __name__ == "__main__":
    unittest.main(verbosity=2)