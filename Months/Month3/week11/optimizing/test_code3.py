import unittest
import time
from ideal_code import lagrangian_relaxation, X, Y, color, cost, P, z

class TestLagrangianRelaxation(unittest.TestCase):

    def test_output_type(self):
        upper_bound, best_solution = lagrangian_relaxation(X, Y, color, cost, P, z)
        self.assertIsInstance(upper_bound, (int, float), "Upper bound should be a number (int or float)")
        self.assertTrue(isinstance(best_solution, dict) or best_solution is None)

    def test_upper_bound(self):
        upper_bound, _ = lagrangian_relaxation(X, Y, color, cost, P, z)
        self.assertGreaterEqual(upper_bound, 0, "Upper bound should be non-negative")

    def test_solution_structure(self):
        _, best_solution = lagrangian_relaxation(X, Y, color, cost, P, z)
        if best_solution is not None:
            for key, value in best_solution.items():
                self.assertIsInstance(key, tuple)
                self.assertEqual(len(key), 3, "Solution key should be a tuple of length 3")
                self.assertIsInstance(value, (int, float), "Solution value should be a number (int or float)")

    def test_feasibility(self):
        _, best_solution = lagrangian_relaxation(X, Y, color, cost, P, z)
        if best_solution is not None:
            for (u, v, p), flow in best_solution.items():
                self.assertIn((u, v), Y, f"Arc ({u}, v) is not in the original network")
                self.assertIn(p, P, f"Commodity {p} is not valid")
                self.assertNotEqual(p, z, f"Commodity {p} should not be equal to z")
                self.assertGreaterEqual(flow, 0, f"Flow {flow} should be non-negative")
                self.assertLessEqual(flow, 1, f"Flow {flow} should be at most 1")

    def test_performance(self):
        start_time = time.time()
        lagrangian_relaxation(X, Y, color, cost, P, z)
        end_time = time.time()
        self.assertLess(end_time - start_time, 10, "Algorithm took too long to execute")

    def test_invalid_inputs(self):
        invalid_inputs = [
            ({}, Y, color, cost, P, z),  # Empty X
            (X, {}, color, cost, P, z),  # Empty Y
            (X, Y, {}, cost, P, z),      # Empty color
            (X, Y, color, {}, P, z),     # Empty cost
            (X, Y, color, cost, [], z),  # Empty P
        ]
        for invalid_input in invalid_inputs:
            try:
                result = lagrangian_relaxation(*invalid_input)
                self.assertIsNone(result[1], f"Expected None solution for invalid input: {invalid_input}")
            except Exception as e:
                pass  # An exception is also acceptable for invalid inputs

    def test_consistency(self):
        upper_bound1, solution1 = lagrangian_relaxation(X, Y, color, cost, P, z)
        upper_bound2, solution2 = lagrangian_relaxation(X, Y, color, cost, P, z)
        self.assertEqual(upper_bound1, upper_bound2, "Algorithm should produce consistent upper bounds")
        self.assertEqual(solution1, solution2, "Algorithm should produce consistent solutions")

    def test_flow_conservation(self):
        _, best_solution = lagrangian_relaxation(X, Y, color, cost, P, z)
        if best_solution is not None:
            for p in P:
                if p != z:
                    for v in X:
                        inflow = sum(best_solution.get((u, v, p), 0) for u in X if (u, v) in Y)
                        outflow = sum(best_solution.get((v, w, p), 0) for w in X if (v, w) in Y)
                        if v == p:
                            self.assertAlmostEqual(inflow - outflow, 1, msg=f"Flow conservation violated at node {v} for commodity {p}")
                        elif v == z:
                            self.assertAlmostEqual(inflow - outflow, -1, msg=f"Flow conservation violated at node {v} for commodity {p}")
                        else:
                            self.assertAlmostEqual(inflow, outflow, msg=f"Flow conservation violated at node {v} for commodity {p}")

if __name__ == '__main__':
    unittest.main(verbosity=2)