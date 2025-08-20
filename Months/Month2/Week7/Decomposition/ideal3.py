import gurobipy as gp
from gurobipy import GRB
import numpy as np
from scipy.sparse import csr_matrix
import time

def decomposition_model(values, cluster_size, Q, p, r, max_iter=100, tol=1e-6):
    n_values = len(values)
    n_clusters = len(cluster_size)

    if sum(cluster_size) < n_values or any(size <= 0 for size in cluster_size):
        print("Problem is infeasible due to insufficient cluster capacity.")
        return None, None

    def create_master_problem():
        master = gp.Model("master_problem")
        master.Params.OutputFlag = 0
        x = master.addMVar((n_values * n_clusters), vtype=GRB.BINARY, name="x")
        
        A1 = csr_matrix((np.ones(n_values * n_clusters), 
                         (np.repeat(np.arange(n_values), n_clusters), np.arange(n_values * n_clusters))), 
                        shape=(n_values, n_values * n_clusters))
        A2 = csr_matrix((np.ones(n_values * n_clusters), 
                         (np.tile(np.arange(n_clusters), n_values), np.arange(n_values * n_clusters))), 
                        shape=(n_clusters, n_values * n_clusters))
        
        master.addConstr(A1 @ x == 1, name="assignment")
        master.addConstr(A2 @ x >= 1, name="coverage")
        
        for j in range(n_clusters):
            master.addConstr(gp.quicksum(x[i*n_clusters + j] for i in range(n_values)) <= cluster_size[j], name=f"capacity_{j}")
        
        return master, x, A1, A2

    def solve_subproblem(x_k, A1, A2):
        sub = gp.Model("subproblem")
        sub.Params.OutputFlag = 0
        y = sub.addMVar((n_values * n_clusters), lb=0, ub=1, vtype=GRB.CONTINUOUS, name="y")
        
        grad = Q @ x_k + p
        obj = grad @ (y - x_k)
        sub.setObjective(obj, GRB.MINIMIZE)
        
        sub.addConstr(A1 @ y == 1, name="assignment")
        sub.addConstr(A2 @ y >= 1, name="coverage")
        for j in range(n_clusters):
            sub.addConstr(gp.quicksum(y[i*n_clusters + j] for i in range(n_values)) <= cluster_size[j], name=f"capacity_{j}")
        
        sub.optimize()
        if sub.Status != GRB.OPTIMAL:
            return None
        return y.X

    def add_gomory_cuts(model):
        cuts_added = 0
        for c in model.getConstrs():
            if c.Sense == '=':
                slack = c.Slack
                if abs(slack) > 1e-6:
                    cut = gp.LinExpr()
                    for v, coef in model.getRow(c).items():
                        frac_coef = coef - np.floor(coef)
                        if frac_coef > 1e-6:
                            cut += frac_coef * v
                    model.addConstr(cut >= slack - np.floor(slack), name=f"gomory_cut_{c.ConstrName}")
                    cuts_added += 1
        return cuts_added

    master, x, A1, A2 = create_master_problem()
    best_obj = float('inf')
    best_sol = None

    for iteration in range(max_iter):
        master.optimize()
        
        if master.Status != GRB.OPTIMAL:
            print(f"Master problem optimization failed at iteration {iteration}.")
            break
        
        current_obj = master.ObjVal
        current_sol = x.X
        
        if current_obj < best_obj:
            best_obj = current_obj
            best_sol = current_sol.copy()
        
        y_k = solve_subproblem(current_sol, A1, A2)
        
        if y_k is None:
            print(f"Subproblem optimization failed at iteration {iteration}.")
            break
        
        if np.linalg.norm(y_k - current_sol) < tol:
            print(f"Converged at iteration {iteration}.")
            break
        
        master.addConstr(0.5 * x @ Q @ x + p @ x + r <= 
                         0.5 * current_sol @ Q @ current_sol + p @ current_sol + r + 
                         (Q @ current_sol + p) @ (x - current_sol), name=f"cut_{iteration}")
        
        cuts_added = add_gomory_cuts(master)
        print(f"Iteration {iteration}: Obj = {current_obj:.6f}, Gomory cuts added = {cuts_added}")
    
    return best_sol, best_obj

# Example usage
values = [1, 2, 3, 4, 5]
cluster_size = [2, 3]
Q = np.random.rand(len(values) * len(cluster_size), len(values) * len(cluster_size))
Q = (Q + Q.T) / 2  # Ensure Q is symmetric
p = np.random.rand(len(values) * len(cluster_size))
r = 1.0

start_time = time.time()
best_solution, best_objective = decomposition_model(values, cluster_size, Q, p, r)
end_time = time.time()

print(f"Final best solution: {best_solution}")
print(f"Final best objective: {best_objective}")
print(f"Total runtime: {end_time - start_time:.2f} seconds")
