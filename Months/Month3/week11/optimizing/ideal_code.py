import gurobipy as gb
import math

# Network data (unchanged)
X = [0, 1, 2, 3, 4]
Y = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 3), (2, 3), (2, 4), (3, 4)]
color = {(0, 1): 0, (0, 2): 0, (0, 3): 3, (1, 4): 7, (1, 3): 4, (2, 3): 5, (2, 4): 6, (3, 4): 7}
cost = {(0, 1): 1, (0, 2): 1, (0, 3): 6, (1, 4): 1, (1, 3): 4, (2, 3): 3, (2, 4): 2, (3, 4): 1}
P = [0, 3, 4]
z = 0

def lagrangian_relaxation(X, Y, color, cost, P, z):
    lamda = {(u, v, p): 0 for p in P if p != z for (u, v) in Y}
    upper_bound = float('inf')
    lower_bound = float('-inf')
    best_solution = None
    P_minus = [p for p in P if p != z]
    step_size = 0.1
    
    for iteration in range(100):
        subproblem = solve_subproblem(X, Y, color, cost, P, z, lamda)
        
        if subproblem.Status == gb.GRB.OPTIMAL:
            obj_value = subproblem.ObjVal
            lower_bound = max(lower_bound, obj_value)
            
            solution = extract_solution(subproblem, Y, P)
            feasible_cost = calculate_feasible_cost(solution, cost)
            if feasible_cost < upper_bound:
                upper_bound = feasible_cost
                best_solution = solution
            
            subgradient = calculate_subgradient(subproblem, Y, P_minus)
            lamda = update_multipliers(lamda, subgradient, step_size, upper_bound, lower_bound)
        else:
            print(f"Unexpected model status in iteration {iteration}: {subproblem.Status}")
        
        step_size *= 0.95
        print(f"Iteration {iteration}: LB = {lower_bound:.2f}, UB = {upper_bound:.2f}")
        
        if upper_bound - lower_bound < 1e-4:
            break
    
    return upper_bound, best_solution

def solve_subproblem(X, Y, color, cost, P, z, lamda):
    model = gb.Model("Lagrangian Relaxation Subproblem")
    model.Params.OutputFlag = 0
    
    y = model.addVars(Y, vtype=gb.GRB.BINARY, name="y")
    f = model.addVars(Y, P, lb=0.0, ub=1.0, name="f")
    
    # Objective: minimize cost + Lagrangian terms
    model.setObjective(
        gb.quicksum(cost[arc] * y[arc] for arc in Y) + 
        gb.quicksum(lamda[u, v, p] * (f[u, v, p] - y[u, v]) for (u, v) in Y for p in P if p != z),
        gb.GRB.MINIMIZE
    )
    
    # Flow conservation
    for v in X:
        for p in P:
            if p != z:
                if v == p:
                    model.addConstr(
                        gb.quicksum(f[u, v, p] for u in X if (u, v) in Y) -
                        gb.quicksum(f[v, w, p] for w in X if (v, w) in Y) == 1
                    )
                elif v == z:
                    model.addConstr(
                        gb.quicksum(f[u, v, p] for u in X if (u, v) in Y) -
                        gb.quicksum(f[v, w, p] for w in X if (v, w) in Y) == -1
                    )
                else:
                    model.addConstr(
                        gb.quicksum(f[u, v, p] for u in X if (u, v) in Y) ==
                        gb.quicksum(f[v, w, p] for w in X if (v, w) in Y)
                    )
    
    # Rainbow constraints
    for c in set(color.values()):
        model.addConstr(gb.quicksum(y[arc] for arc in Y if color[arc] == c) <= 1)
    
    # Linking constraints
    for (u, v) in Y:
        for p in P:
            if p != z:
                model.addConstr(f[u, v, p] <= y[u, v])
    
    model.optimize()
    return model

def calculate_subgradient(model, Y, P_minus):
    y = model.getAttr('X', model.getVars())
    f = {(u, v, p): model.getVarByName(f"f[{u},{v},{p}]").X for (u, v) in Y for p in P_minus}
    return {(u, v, p): f[u, v, p] - y[Y.index((u, v))] for (u, v) in Y for p in P_minus}

def update_multipliers(lamda, subgradient, step_size, upper_bound, lower_bound):
    norm = math.sqrt(sum(g**2 for g in subgradient.values()))
    if norm > 0:
        factor = step_size * (upper_bound - lower_bound) / norm
        return {key: max(0, lamda[key] + factor * subgradient[key]) for key in lamda}
    return lamda

def extract_solution(model, Y, P):
    return {(u, v, p): model.getVarByName(f"f[{u},{v},{p}]").X 
            for (u, v) in Y for p in P if p != z}

def calculate_feasible_cost(solution, cost):
    return sum(cost[u, v] for (u, v, p), flow in solution.items() if flow > 1e-6)

# Run the algorithm
best_upper_bound, best_solution = lagrangian_relaxation(X, Y, color, cost, P, z)
print(f"Best Upper Bound: {best_upper_bound:.2f}")
print("Best Solution:")
if best_solution:
    for (u, v, p), flow in best_solution.items():
        if flow > 1e-6:
            print(f"Flow from {u} to {v} for commodity {p}: {flow:.2f}")
else:
    print("No feasible solution found.")