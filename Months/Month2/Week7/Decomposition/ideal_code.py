import gurobipy as gp
from gurobipy import GRB
import numpy as np
import time

def decomposition_model(values, cluster_size, Q, p, r, max_iter=100, tol=1e-6):
    n_values = len(values)
    n_clusters = len(cluster_size)
    n_vars = n_values * n_clusters

    # Check for obvious infeasibility
    if sum(cluster_size) > n_values:
        print("Problem is infeasible: sum of cluster sizes exceeds number of values")
        return None, None

    # Initialize the master problem
    master = gp.Model("master_problem")
    master.Params.OutputFlag = 0
    master.Params.MIPGap = 1e-4

    # Define variables as binary
    x = master.addMVar(n_vars, vtype=GRB.BINARY, name="x")

    # Set constraints
    A1 = np.kron(np.eye(n_values), np.ones(n_clusters))
    A2 = np.kron(np.ones(n_values), np.eye(n_clusters))
    master.addConstr(A1 @ x == 1, name="c1")
    master.addConstr(A2 @ x >= 1, name="c2")

    # Set objective
    obj = 0.5 * x @ Q @ x + p @ x + r
    master.setObjective(obj, GRB.MINIMIZE)

    # Callback function for lazy constraints (cuts)
    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            x_val = model.cbGetSolution(model._vars)
            # Add cuts based on the current integer solution
            # This is where you would implement problem-specific cuts

    master._vars = x
    master.Params.LazyConstraints = 1

    # Solve the problem
    start_time = time.time()
    master.optimize(callback)
    
    if master.Status != GRB.OPTIMAL:
        print("Optimization failed or problem is infeasible.")
        return None, None

    x_best = x.X
    f_best = master.ObjVal

    end_time = time.time() - start_time
    print(f"Total time: {end_time:.2f} seconds")
    print(f"Best binary objective: {f_best}")

    return x_best, f_best