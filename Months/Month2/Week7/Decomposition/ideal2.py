import gurobipy as gp
from gurobipy import GRB
import numpy as np
import time

def improved_decomposition_model(values, cluster_size, Q, p, r, max_time=300, mip_gap=0.01):
    # Define model
    model = gp.Model("qp_binary_allocation")
    model.Params.LogToConsole = 1  # Enable console output for monitoring
    model.Params.TimeLimit = max_time  # Set maximum runtime in seconds
    model.Params.MIPGap = mip_gap  # Set the MIP gap tolerance

    n_values = len(values)
    n_clusters = len(cluster_size)

    # Define binary variables
    x = model.addMVar((n_values, n_clusters), vtype=GRB.BINARY, name="x")

    # Set the constraints
    # Each value must be assigned to exactly one cluster
    model.addConstrs((gp.quicksum(x[i, j] for j in range(n_clusters)) == 1
                      for i in range(n_values)), name="value_assignment")

    # Each cluster must have at least one value assigned
    model.addConstrs((gp.quicksum(x[i, j] for i in range(n_values)) >= 1
                      for j in range(n_clusters)), name="cluster_non_empty")

    # Define the objective function
    obj = 0.5 * x.reshape(1, -1) @ Q @ x.reshape(-1, 1) + p @ x.reshape(-1, 1) + r
    model.setObjective(obj, sense=GRB.MINIMIZE)

    # Set up callback for custom cuts (if needed)
    def custom_cut_callback(model, where):
        if where == GRB.Callback.MIPSOL:
            x_val = model.cbGetSolution(model._vars)
            # Add custom cuts here if needed
            # Example: model.cbCut(your_custom_cut_expression >= 0)

    model._vars = x
    model.Params.LazyConstraints = 1

    # Optimize the model
    start_time = time.time()
    model.optimize(custom_cut_callback)
    solve_time = time.time() - start_time

    # Process results
    if model.Status == GRB.OPTIMAL:
        x_sol = x.X
        obj_val = model.ObjVal
        print(f"Optimal solution found. Objective value: {obj_val}")
    elif model.Status == GRB.TIME_LIMIT:
        x_sol = x.X
        obj_val = model.ObjVal
        print(f"Time limit reached. Best objective value found: {obj_val}")
    else:
        print(f"Optimization was stopped with status {model.Status}")
        return None

    # Reshape solution to 2D array for easier interpretation
    x_sol_reshaped = x_sol.reshape(n_values, n_clusters)

    return x_sol_reshaped, obj_val, solve_time

# Example usage:
# values = [1, 2, 3, 4, 5]
# cluster_size = [2, 3]
# Q = np.random.rand(5*2, 5*2)  # Example random Q matrix
# Q = (Q + Q.T) / 2  # Ensure Q is symmetric
# p = np.random.rand(5*2)  # Example random p vector
# r = 0  # Example constant term
# 
# solution, objective, runtime = improved_decomposition_model(values, cluster_size, Q, p, r)
# 
# if solution is not None:
#     print("Solution:")
#     print(solution)
#     print(f"Objective value: {objective}")
#     print(f"Solve time: {runtime} seconds")