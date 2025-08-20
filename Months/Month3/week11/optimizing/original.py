import heapq
import random
import gurobipy as gb

# Node and arc data
X = [0, 1, 2, 3, 4]
Y = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 3), (2, 3), (2, 4), (3, 4)]  # List of arcs
color = {(0, 1): 0, (0, 2): 0, (0, 3): 3, (1, 4): 7, (1, 3): 4, (2, 3): 5, (2, 4): 6, (3, 4): 7}  # Arc colors
cost = {(0, 1): 1, (0, 2): 1, (0, 3): 6, (1, 4): 1, (1, 3): 4, (2, 3): 3, (2, 4): 2, (3, 4): 1}  # Arc costs
P = [0, 3, 4]  # Terminal nodes
z = 0  # Source node
zeta_ = 0.1

def lagrangian_relaxation(X, Y, color, cost, P, z):
    lamda = {}

    # Start with the upper limit set to infinity
    upper_limit = float('inf')

    P_exclude = [point for point in P if point != z]

    # Lagrange multiplier setup
    for point in P_exclude:
        for (u, v) in Y:
            lamda[u, v, point] = cost[(u, v)]

    rounds = 0
    max_rounds = 100

    while rounds <= max_rounds:
        # Implement primary methods
        conveyance_info = R1(X, Y, color, cost, P, z)
        chosen_links = R2(X, Y, color, cost, P, z, lamda)

        # Generate reciprocal arcs
        Z = Y + [(v, u) for (u, v) in Y]  # Including backward arcs
        cost_bidirection = cost.copy()
        color_bidirection = color.copy()

        # Set up backward arc expenses
        for (u, v) in Y:
            cost_bidirection[(v, u)] = cost[(u, v)]
            color_bidirection[(v, u)] = color[(u, v)]

        # Revise based on conveyance outcomes
        update_chosen(conveyance_info, Z, chosen_links)

        # Draft sub-structure
        memberships, Z_origin, color_origin, Y_origin = draft_substructure(Z, chosen_links)

        # Process the Lagrangian Relaxation model
        execute_Lagrange_Relaxation(memberships, Y_origin, color_origin, Z_origin, P, z)

        # Adjust the upper boundary if a preferable model is identified
        if execute_Lagrange_Relaxation.model.objVal < upper_limit:
            upper_limit = execute_Lagrange_Relaxation.model.objVal

        # Refresh Lagrange multipliers (lamda)
        lamda_next = modify_dual(lamda, P_exclude, Y_origin, chosen_links, cost, Z_origin, color_origin)

        # Move forward with updated lamda values
        lamda = lamda_next

        rounds += 1

    return upper_limit

def R1(X, Y, color, cost, P, z):
    # Generate reciprocal arcs
    Z = Y + [(v, u) for (u, v) in Y]  # Including backward arcs
    cost_bidirection = cost.copy()

    for (u, v) in Y:
        cost_bidirection[(v, u)] = cost[(u, v)]

    # Implement Dijkstra's method to compute briefest paths and fluxes
    source = random.choice(P)
    path_distances, prior = dij_recursion(source, X, Z, cost_bidirection)

    conveyance_data = {}
    for point in P:
        if point != source:
            path, flux = redraw_path_with_convey(prior, point, Z)
            conveyance_data[point] = flux

    return conveyance_data

def R2(X, Y, color, cost, P, z, lamda):
    # Generate reciprocal arcs
    Z = Y + [(v, u) for (u, v) in Y]

    # Compute lessened expenses and determine links based on least lessened expenses
    cost_bidirection = cost.copy()
    color_bidirection = color.copy()

    for (u, v) in Y:
        cost_bidirection[(v, u)] = cost[(u, v)]
        color_bidirection[(v, u)] = color[(u, v)]

    # Initialize selected arc list in Z
    selected = {arc: 0 for arc in Z}
    map_of_colors = {shade: [path for path in color_bidirection if color_bidirection[path] == shade] for shade in set(color_bidirection.values())}

    chosen_links, lessened_expense = initiate_R1(Z, cost_bidirection, lamda, map_of_colors)
    return chosen_links

def execute_Lagrange_Relaxation(memberships, Y_origin, color_origin, Z_origin, P, z):
    umr = gb.Model("Lagrangian Relaxation")

    # Decision variables
    selected = umr.addVars(Y_origin, vtype=gb.GRB.BINARY, name="selected")
    conveyance = umr.addVars(Z_origin, P, lb=0.0, name="conveyance")

    # Objective function
    umr.setObjective(gb.quicksum(Z_origin[path] * selected[path] for path in Y_origin), gb.GRB.MINIMIZE)

    # Flux conservation factors
    for u in memberships:
        for point in P:
            umr.addConstr(gb.quicksum(conveyance[u, v, point] for v in memberships if (u, v) in Z_origin) -
                          gb.quicksum(conveyance[v, u, point] for v in memberships if (v, u) in Z_origin) == (1 if u == z else -1 if u == point else 0))

    # Bound-linking constraints
    for (u, v) in Y_origin:
        for point in P:
            umr.addConstr(conveyance[u, v, point] <= selected[u, v])

    # Condition for Rainbow criterion
    for coloring_val in set(color_origin.values()):
        umr.addConstr(gb.quicksum(selected[path] for path in Y_origin if color_origin.get(path) == coloring_val) <= 1)

    umr.optimize()

    return umr

def update_chosen(conveyance_data, Z, selected):
    for point, convey in conveyance_data.items():
        for (u, v), flux_val in convey.items():
            if flux_val > 0:
                selected[(u, v)] = 1

def draft_substructure(Z, selected):
    memberships = set()
    Z_origin = {}
    color_origin = {}
    Y_origin = set()

    for (u, v) in Z:
        if selected.get((u, v), 0) == 1:
            memberships.add(u)
            memberships.add(v)
            unordered_link = (min(u, v), max(u, v))
            if unordered_link not in Z_origin:
                Z_origin[unordered_link] = cost[(u, v)]
                color_origin[unordered_link] = color[(u, v)]
                Y_origin.add(unordered_link)

    return list(memberships), Z_origin, color_origin, list(Y_origin)

def modify_dual(lamda, P_exclude, Y_origin, selected, cost, Z_origin, color_origin):
    lamda_next = {}
    for point in P_exclude:
        for (u, v) in Y_origin:
            if all(selected[(u, v)] == 0 for point in P_exclude):
                mu_shift_ = min(Z_origin[path] for path in Y_origin) - (cost[(u, v)] - sum(lamda[(u, v, point)] for point in P_exclude))
                for point in P_exclude:
                    lamda_next[u, v, point] = max(lamda[u, v, point] - mu_shift_ / len(P_exclude), 0)

    return lamda_next

# Auxiliary methods for Dijkstra and reconveyance
def dij_recursion(source, X, Z, cost):
    distances = {v: float('inf') for v in X}  # Start distances at infinity
    distances[source] = 0
    prior = {v: None for v in X}  # Mark previous point for path reconstruction
    queue = [(0, source)]  # Primary queue with (distance, node)

    while queue:
        distance, nodefetch = heapq.heappop(queue)

        if distance > distances[nodefetch]:
            continue

        for (u_fetch, v_fetch) in Z:
            if u_fetch == nodefetch:  # Consider arcs beginning from nodefetch
                alternative = distances[nodefetch] + cost[(nodefetch, v_fetch)]
                if alternative < distances[v_fetch]:  # Shorter path acknowledged
                    distances[v_fetch] = alternative
                    prior[v_fetch] = nodefetch
                    heapq.heappush(queue, (alternative, v_fetch))

    return distances, prior

def redraw_path_with_convey(prior, destination, Z):
    path = []
    conveyance = {(u, v): 0 for (u, v) in Z}  # Set initial conveyance for every arc as 0
    while destination is not None:
        path.insert(0, destination)
        if prior[destination] is not None:
            starting, ending = prior[destination], destination
            conveyance[(starting, ending)] = 1  # Link (starting, ending) utilized in path, thus conveyance as 1
        destination = prior[destination]
    return path, conveyance
