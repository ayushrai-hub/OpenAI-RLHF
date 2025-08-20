import gurobipy as gp
from gurobipy import GRB
import numpy as np
import time

def decomposition_model(values, cluster_size, Q, p, r, max_iter=1, tol=0.1):
    history = []
    save_x = []

    # Define model
    model = gp.Model("qp_allocation")
    model.Params.LogToConsole = 0
    model.Params.Presolve = 2
    model.Params.Method = 2
    model.setParam('FeasibilityTol', 1e-6)
    model.setParam('OptimalityTol', 1e-6)
    model.setParam('IntFeasTol', 1e-6)

    n_values = len(values)
    n_clusters = len(cluster_size)

    x = model.addMVar((n_values * n_clusters), lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x")

    # Set the linear constraints
    A1 = np.kron(np.eye(n_values), np.ones((1, n_clusters)))
    A2 = np.kron(np.ones((1, n_values)), np.eye(n_clusters))
    b1 = np.ones(n_values)
    b2 = np.ones(n_clusters)
    model.addConstr(A1 @ x == b1, name="c1")
    model.addConstr(A2 @ x >= b2, name="c2")

    # Initial solution from continuous relaxation
    obj1 = 0.5 * x @ Q @ x + p @ x + r
    model.setObjective(obj1, sense=GRB.MINIMIZE)

    start_time = time.time()
    model.optimize()
    end_time = time.time() - start_time

    if model.Status != GRB.OPTIMAL:
        print("Optimization was not successful.")
        return None

    x_k = x.X
    f = model.ObjVal

    x_round = np.where(x_k >= 0.5, 1.0, 0.0)
    f_round = 0.5 * x_round @ Q @ x_round + p @ x_round + r

    print(f"Initial f: {f}, rounded f: {f_round}")

    # For saving purpose
    best_binary_result = f_round
    best_binary_solution = x_round

    def add_gomory_cuts(m, x_vals):
        for j in range(len(x_vals)):
            fractional_part = x_vals[j] - np.floor(x_vals[j])
            if 1e-6 < fractional_part < 1 - 1e-6:
                lhs_expr = gp.LinExpr()
                for c in m.getConstrs():
                    coeff = m.getCoeff(c, x[j])
                    lhs_expr += (coeff - np.floor(coeff)) * x[j]
                m.addConstr(lhs_expr >= fractional_part, name=f"gomory_cut_{j}")

    for iteration in range(max_iter):
        if np.all(np.isin(x_k, [0, 1])):
            print("The master problem results are all binary solutions.")
            break
        else:
            bmodel = gp.Model("linear_approximation_model")
            bmodel.Params.LogToConsole = 0
            bmodel.Params.Method = 0

            x_new = bmodel.addMVar((n_values * n_clusters), lb=0, ub=1, vtype=GRB.CONTINUOUS, name="x_new")
            
            grad = Q @ x_k + p
            b_obj = grad @ (x_new - x_k)
            bmodel.setObjective(b_obj, GRB.MINIMIZE)

            bmodel.addConstr(A1 @ x_new == b1, name="c1")
            bmodel.addConstr(A2 @ x_new >= b2, name="c2")

            bmodel.optimize()

            if bmodel.Status != GRB.OPTIMAL:
                print("Subproblem optimization failed.")
                break

            x_k_new = x_new.X
            g = 0.5 * x_k_new @ Q @ x_k_new + p @ x_k_new + r
            alpha = 1.0

            while g > f and alpha > 1e-6:
                x_k_new = x_k + alpha * (x_k_new - x_k)
                g = 0.5 * x_k_new @ Q @ x_k_new + p @ x_k_new + r
                alpha *= 0.5

            print(f"Iteration {iteration + 1}, g: {g}, alpha: {alpha}")

            if np.linalg.norm(g - f) <= tol:
                print("Convergence criterion met.")
                break

            if np.any((x_k_new - np.floor(x_k_new)) > 1e-6):
                add_gomory_cuts(model, x_k_new)
            
            if np.all(np.isin(x_k_new, [0, 1])):
                if g < best_binary_result:
                    best_binary_result = g
                    best_binary_solution = x_k_new.copy()
                break

            x_k = x_k_new
            f = g
            history.append(g)
            save_x.append(x_k)

    return best_binary_solution, best_binary_result

# Example Usage:
# values = [some values]
# cluster_size = [some cluster sizes]
# Q = np.array([...])  # Define Q matrix
# p = np.array([...])  # Define p vector
# r = some constant value
# decomposition_model(values, cluster_size, Q, p, r)
