import unittest
import random

# Assuming that the 'aco_solver' function and related dependencies are defined in 'ideal_completion.py'
from ideal_completion import aco_solver, heuristic_prioritize_demand, calculate_expected_demand

class TestACOSolver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set a fixed random seed for reproducibility
        random.seed(42)

    def test_aco_solver_returns_route_and_distance(self):
        # Test if aco_solver returns a tuple with best_route and best_distance
        result = aco_solver()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        best_route, best_distance = result
        self.assertIsInstance(best_route, list)
        self.assertIsInstance(best_distance, float)

    def test_aco_solver_demand_priority(self):
        # Test if the route visits high-demand locations before others
        best_route, _ = aco_solver()
        # Mock expected demands for locations
        demands = {'A': 50, 'B': 30, 'C': 20, 'D': 10}
        # Extract visited venues excluding the depot 'W'
        visited_venues = [loc for loc in best_route if loc != 'W']
        # Map venues to their demands
        visited_demands = [demands[loc] for loc in visited_venues]
        # Check if demands are in descending order
        self.assertEqual(visited_demands, sorted(visited_demands, reverse=True))

    def test_heuristic_prioritize_demand(self):
        # Test if heuristic function correctly prioritizes higher demand over distance
        # Mock demands and distances
        global calculate_expected_demand
        def mock_calculate_expected_demand(location):
            mock_demands = {'A': 50, 'B': 30}
            return mock_demands[location]

        global distances
        distances = {('X', 'A'): 10, ('X', 'B'): 2}

        # Replace the real function with the mock
        original_calculate_expected_demand = calculate_expected_demand
        calculate_expected_demand = mock_calculate_expected_demand

        eta_A = heuristic_prioritize_demand('X', 'A')
        eta_B = heuristic_prioritize_demand('X', 'B')

        # Higher demand location 'A' should have a higher heuristic value despite longer distance
        self.assertGreater(eta_A, eta_B)

        # Restore the original function
        calculate_expected_demand = original_calculate_expected_demand

if __name__ == "__main__":
    unittest.main(verbosity=2)
