import unittest
import gurobipy as gb
import io
from contextlib import redirect_stdout, redirect_stderr
from testableIC import LR1, LR2, update_x_based_on_flow, build_subgraph, solve_Lagrange_Relaxtion, Lagrangian_Relaxation

class TestLagrangianRelaxation(unittest.TestCase):

    def setUp(self):
        # Initial setup of input data for testing different scenarios
        self.VERTICES = [1, 2, 3, 4, 5]
        self.EDGES = [
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (1, 5),
            (2, 5)
        ]
        self.weights = {
            (1, 2): 'red',
            (2, 3): 'blue',
            (3, 4): 'red',
            (4, 5): 'blue',
            (1, 5): 'green',
            (2, 5): 'green'
        }
        self.costs = {
            (1, 2): 4,
            (2, 3): 3,
            (3, 4): 5,
            (4, 5): 2,
            (1, 5): 7,
            (2, 5): 6
        }
        self.terminals = [1, 3, 5]
        self.source = 1
        self.mult = {
            (1, 2, 3): 2,
            (2, 3, 3): 1,
            (3, 4, 3): 0,
            (1, 5, 3): 1,
            (2, 5, 3): 2
        }
        
        # Suppress stdout and stderr to ensure clean test output
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self._redirect_stdout = redirect_stdout(self.stdout)
        self._redirect_stderr = redirect_stderr(self.stderr)
        self._redirect_stdout.__enter__()
        self._redirect_stderr.__enter__()

    def tearDown(self):
        # Stop suppressing stdout and stderr after each test
        self._redirect_stdout.__exit__(None, None, None)
        self._redirect_stderr.__exit__(None, None, None)

    def suppress_gurobi_logging(self):
        # Suppresses all Gurobi logs to prevent clutter in test output
        gb.setParam('OutputFlag', 0)
        gb.setParam('LogFile', '')

    def test_LR1(self):
        # Verifies that the Dijkstra-based shortest path and flow details are correctly computed for terminals.
        # Ensures that the flow information for each terminal (excluding the source) is accurately determined.
        self.suppress_gurobi_logging()
        flow_details = LR1(self.VERTICES, self.EDGES, self.weights, self.costs, self.terminals, self.source)
        self.assertIsInstance(flow_details, dict)
        # Checks that all terminal nodes (except source) have valid flow entries in the results
        for target in self.terminals:
            if target != self.source:
                self.assertIn(target, flow_details)
                self.assertIsInstance(flow_details[target], dict)

    def test_LR2(self):
        # Validates the selection of reduced cost edges based on Lagrangian multipliers.
        # Ensures that the correct edges are selected as part of the optimal solution set.
        self.suppress_gurobi_logging()
        selected_edges, weight_map = LR2(self.VERTICES, self.EDGES, self.weights, self.costs, self.terminals, self.source, self.mult)
        self.assertIsInstance(selected_edges, dict)
        # Verifies that selected edges match the weight categories they belong to
        for edge in self.EDGES:
            self.assertIn(edge, selected_edges)
            self.assertIn(edge, weight_map[self.weights[edge]])

    def test_update_x_based_on_flow(self):
        # Tests that edges with positive flow are marked correctly in the decision variable `x`.
        # Ensures that edges used in the optimal flow have their selection variable updated.
        self.suppress_gurobi_logging()
        flow_details = {
            5: {(1, 2): 1, (2, 3): 0, (3, 4): 1, (4, 5): 0, (1, 5): 1, (2, 5): 0}
        }
        x = {edge: 0 for edge in self.EDGES + [(end, start) for (start, end) in self.EDGES]}
        update_x_based_on_flow(flow_details, self.EDGES, x)
        # Ensures `x` reflects positive flow values accurately for selected edges
        for edge, flow_value in flow_details[5].items():
            if flow_value > 0:
                self.assertEqual(x[edge], 1)

    def test_build_subgraph(self):
        # Tests that the subgraph is built correctly from the selected edges.
        # Ensures the correct extraction of nodes, edges, and their costs into a subgraph for further optimization.
        self.suppress_gurobi_logging()
        selected_edges = {
            (1, 2): 1,
            (2, 3): 0,
            (3, 4): 1,
            (4, 5): 0,
            (1, 5): 1,
            (2, 5): 0
        }
        nodes_set, arcs_cost, weights_cost, edge_set = build_subgraph(
            self.EDGES + [(end, start) for (start, end) in self.EDGES],
            selected_edges, self.costs, self.weights
        )
        # Confirms that the correct nodes and edges are part of the constructed subgraph
        self.assertIn(1, nodes_set)
        self.assertIn(2, nodes_set)
        self.assertIn(5, nodes_set)
        self.assertIn((1, 2), edge_set)
        self.assertIn((1, 5), edge_set)

    def test_solve_Lagrange_Relaxtion(self):
        # Validates that the Lagrangian relaxation problem is correctly formulated and solved to optimality.
        # Ensures that the optimization model reaches an optimal solution and respects all constraints.
        self.suppress_gurobi_logging()
        arcs_cost = {edge: self.costs[edge] for edge in self.EDGES}
        model = solve_Lagrange_Relaxtion(self.VERTICES, self.EDGES, arcs_cost, arcs_cost, self.terminals, self.source)
        self.assertEqual(model.status, gb.GRB.OPTIMAL)

    def test_Lagrangian_Relaxation(self):
        # Verifies the overall process of Lagrangian relaxation and checks that a valid upper bound is returned.
        # Ensures the algorithm's iterative process converges to a meaningful solution for the upper bound.
        self.suppress_gurobi_logging()
        upper_bound = Lagrangian_Relaxation(self.VERTICES, self.EDGES, self.weights, self.costs, self.terminals, self.source)
        self.assertIsInstance(upper_bound, float)
        self.assertGreater(upper_bound, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)