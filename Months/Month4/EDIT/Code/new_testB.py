import unittest
from ideal_completion import (
    Lagrangian_Relaxation,
    LR1,
    LR2
)

class TestLagrangianRelaxation(unittest.TestCase):
    def setUp(self):
        """Initialize test cases for different scenarios"""
        # Basic test case
        self.basic_vertices = ['A', 'B', 'C']
        self.basic_edges = [('A', 'B'), ('B', 'C'), ('A', 'C')]
        self.basic_weights = {('A', 'B'): 'red', ('B', 'C'): 'green', ('A', 'C'): 'blue'}
        self.basic_costs = {('A', 'B'): 1, ('B', 'C'): 2, ('A', 'C'): 3}
        self.basic_terminals = ['A', 'C']
        self.basic_source = 'A'

        # Large graph test case
        self.large_vertices = [str(i) for i in range(100)]
        self.large_edges = [(str(i), str(i+1)) for i in range(99)]
        self.large_weights = {edge: f'color_{i%5}' for i, edge in enumerate(self.large_edges)}
        self.large_costs = {edge: i+1 for i, edge in enumerate(self.large_edges)}
        self.large_terminals = [str(i) for i in range(0, 100, 10)]
        self.large_source = '0'

        # Disconnected graph test case
        self.disconnected_vertices = ['A', 'B', 'C', 'D', 'E']
        self.disconnected_edges = [('A', 'B'), ('D', 'E')]
        self.disconnected_weights = {('A', 'B'): 'red', ('D', 'E'): 'blue'}
        self.disconnected_costs = {('A', 'B'): 1, ('D', 'E'): 1}
        self.disconnected_terminals = ['A', 'E']

    def test_basic_functionality(self):
        """Test basic functionality with simple graph"""
        upper_bound = Lagrangian_Relaxation(
            self.basic_vertices,
            self.basic_edges,
            self.basic_weights,
            self.basic_costs,
            self.basic_terminals,
            self.basic_source
        )
        self.assertIsInstance(upper_bound, float)
        self.assertGreater(upper_bound, 0)

    def test_solution_optimality(self):
        """Verify solution meets optimality conditions"""
        upper_bound = Lagrangian_Relaxation(
            self.basic_vertices,
            self.basic_edges,
            self.basic_weights,
            self.basic_costs,
            self.basic_terminals,
            self.basic_source
        )
        # Verify upper bound is at least the minimum cost path
        min_path_cost = min(self.basic_costs.values())
        self.assertGreaterEqual(upper_bound, min_path_cost)

    def test_disconnected_graph(self):
        """Test handling of disconnected graphs"""
        with self.assertRaises(ValueError):
            Lagrangian_Relaxation(
                self.disconnected_vertices,
                self.disconnected_edges,
                self.disconnected_weights,
                self.disconnected_costs,
                self.disconnected_terminals,
                None
            )

    def test_convergence(self):
        """Test algorithm convergence"""
        # Run algorithm multiple times to check consistency
        results = []
        for _ in range(5):
            upper_bound = Lagrangian_Relaxation(
                self.basic_vertices,
                self.basic_edges,
                self.basic_weights,
                self.basic_costs,
                self.basic_terminals,
                self.basic_source
            )
            results.append(upper_bound)
        
        # Check that results are consistent within tolerance
        tolerance = 1e-6
        for i in range(1, len(results)):
            self.assertAlmostEqual(results[0], results[i], delta=tolerance)

    def test_component_functions(self):
        """Test individual component functions"""
        # Test LR1
        flow_details = LR1(
            self.basic_vertices,
            self.basic_edges,
            self.basic_weights,
            self.basic_costs,
            self.basic_terminals,
            self.basic_source
        )
        self.assertIsInstance(flow_details, dict)

        # Test LR2
        mult = {(i, j, t): 0 for i, j in self.basic_edges for t in self.basic_terminals}
        weight_map = {}
        for edge, color in self.basic_weights.items():
            if color not in weight_map:
                weight_map[color] = []
            weight_map[color].append(edge)
        
        selected_edges = LR2(
            self.basic_vertices,
            self.basic_edges,
            self.basic_weights,
            self.basic_costs,
            self.basic_terminals,
            self.basic_source,
            mult,
            weight_map
        )
        self.assertIsInstance(selected_edges, dict)

    def test_numerical_stability(self):
        """Test numerical stability with extreme costs"""
        extreme_costs = self.basic_costs.copy()
        extreme_costs[('A', 'B')] = 1e9
        extreme_costs[('B', 'C')] = 1e-9
        
        upper_bound = Lagrangian_Relaxation(
            self.basic_vertices,
            self.basic_edges,
            self.basic_weights,
            extreme_costs,
            self.basic_terminals,
            self.basic_source
        )
        self.assertIsInstance(upper_bound, float)
        self.assertGreater(upper_bound, 0)

if __name__ == '__main__':
    unittest.main()