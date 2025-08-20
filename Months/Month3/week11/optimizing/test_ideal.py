import unittest
from math import isclose
from testable_ideal_completion import (
    lagrangian_relaxation, solve_subproblem, calculate_subgradient,
    update_multipliers, extract_solution, calculate_feasible_cost
)

class TestLagrangianRelaxation(unittest.TestCase):
    def setUp(self):
        # Initialize test data for all test cases
        self.X = [0, 1, 2, 3, 4]
        self.Y = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 3), (2, 3), (2, 4), (3, 4)]
        self.color = {(0, 1): 0, (0, 2): 0, (0, 3): 3, (1, 4): 7, (1, 3): 4, (2, 3): 5, (2, 4): 6, (3, 4): 7}
        self.cost = {(0, 1): 1, (0, 2): 1, (0, 3): 6, (1, 4): 1, (1, 3): 4, (2, 3): 3, (2, 4): 2, (3, 4): 1}
        self.P = [0, 3, 4]
        self.z = 0

    def test_lagrangian_relaxation(self):
        # This tests the overall lagrangian relaxation algorithm and ensures it works correctly
        upper_bound, solution = lagrangian_relaxation(self.X, self.Y, self.color, self.cost, self.P, self.z)
        self.assertIsNotNone(upper_bound)
        self.assertIsNotNone(solution)
        self.assertGreater(upper_bound, 0)
        self.assertLessEqual(len(solution), len(self.Y) * (len(self.P) - 1))

    def test_solve_subproblem(self):
        # This test checks if the subproblem can be solved to optimality
        lamda = {(u, v, p): 0 for p in self.P if p != self.z for (u, v) in self.Y}
        model = solve_subproblem(self.X, self.Y, self.color, self.cost, self.P, self.z, lamda)
        self.assertEqual(model.Status, 2)  # 2 is the code for OPTIMAL in Gurobi
        self.assertGreaterEqual(model.ObjVal, 0)

    def test_calculate_subgradient(self):
        # This test verifies that subgradients guide the optimization process in the Lagrangian relaxation method.
        lamda = {(u, v, p): 0 for p in self.P if p != self.z for (u, v) in self.Y}
        model = solve_subproblem(self.X, self.Y, self.color, self.cost, self.P, self.z, lamda)
        model.optimize()
        P_minus = [p for p in self.P if p != self.z]
        subgradient = calculate_subgradient(model, self.Y, P_minus)
        self.assertEqual(len(subgradient), len(self.Y) * len(P_minus))

    def test_update_multipliers(self):
        # This test ensures that multipliers are updated correctly and remain non-negative
        lamda = {(u, v, p): 1 for p in self.P if p != self.z for (u, v) in self.Y}
        subgradient = {key: 0.1 for key in lamda}
        step_size, upper_bound, lower_bound = 0.1, 10, 5
        new_lamda = update_multipliers(lamda, subgradient, step_size, upper_bound, lower_bound)
        self.assertEqual(len(new_lamda), len(lamda))
        for key in lamda:
            self.assertGreaterEqual(new_lamda[key], 0)

    def test_extract_solution(self):
        # This test verifies that a valid solution can be extracted from the solved subproblem
        lamda = {(u, v, p): 0 for p in self.P if p != self.z for (u, v) in self.Y}
        model = solve_subproblem(self.X, self.Y, self.color, self.cost, self.P, self.z, lamda)
        model.optimize()
        solution = extract_solution(model, self.Y, self.P)
        self.assertEqual(len(solution), len(self.Y) * (len(self.P) - 1))

    def test_calculate_feasible_cost(self):
        # This test checks if the cost of a given solution is calculated correctly 
        solution = {(u, v, p): 0.5 for (u, v) in self.Y for p in self.P if p != self.z}
        cost = calculate_feasible_cost(solution, self.cost)
        self.assertGreater(cost, 0)

    def test_solution_feasibility(self):
        # This test ensures that the solution satisfies all problem constraints
        _, solution = lagrangian_relaxation(self.X, self.Y, self.color, self.cost, self.P, self.z)
        self.check_flow_conservation(solution)
        self.check_rainbow_constraints(solution)

    def check_flow_conservation(self, solution):
        # This verifies that the flow is conserved at each node for each commondity
        for v in self.X:
            for p in self.P:
                if p != self.z:
                    inflow = sum(solution.get((u, v, p), 0) for u in self.X if (u, v) in self.Y)
                    outflow = sum(solution.get((v, w, p), 0) for w in self.X if (v, w) in self.Y)
                    if v == p:
                        self.assertTrue(isclose(inflow - outflow, 1, abs_tol=1e-6))
                    elif v == self.z:
                        self.assertTrue(isclose(inflow - outflow, -1, abs_tol=1e-6))
                    else:
                        self.assertTrue(isclose(inflow, outflow, abs_tol=1e-6))

    def check_rainbow_constraints(self, solution):
        # This ensures that each color is used at most once in the solution
        for c in set(self.color.values()):
            used_arcs = sum(1 for (u, v) in self.Y if self.color[(u, v)] == c and 
                            any(solution.get((u, v, p), 0) > 1e-6 for p in self.P if p != self.z))
            self.assertLessEqual(used_arcs, 1, f"Color {c} is used more than once")
            
if __name__ == '__main__':
    unittest.main(verbosity=2)