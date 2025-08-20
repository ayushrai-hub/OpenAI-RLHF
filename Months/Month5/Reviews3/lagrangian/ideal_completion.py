# ideal_completion.py
import heapq
import random
import gurobipy as gb

def LR1(VERTICES, EDGES, weights, costs, terminals, source):
    # Add bidirectional edges by appending reversed edges with same costs
    arcs = EDGES + [(end, start) for (start, end) in EDGES]
    b_costs = costs.copy()

    # Assign costs for reverse edges
    for (start, end) in EDGES:
        b_costs[(end, start)] = costs[(start, end)]

    # Dijkstra's method with flow computation
    def perform_dijkstra(src, VERTICES, arcs, b_costs):
        min_dist = {node: float('inf') for node in VERTICES}
        min_dist[src] = 0
        previous_nodes = {node: None for node in VERTICES}
        queue = [(0, src)]

        while queue:
            distance, current = heapq.heappop(queue)

            if distance > min_dist[current]:
                continue

            for (node_a, node_b) in arcs:
                if node_a == current:
                    alternative = min_dist[current] + b_costs[(current, node_b)]
                    if alternative < min_dist[node_b]:
                        min_dist[node_b] = alternative
                        previous_nodes[node_b] = current
                        heapq.heappush(queue, (alternative, node_b))

        return min_dist, previous_nodes

    # Recreate path from source to target and compute flow
    def recover_path_and_flow(previous_nodes, target, arcs):
        traversed_path = []
        flow_tracked = {(i, j): 0 for (i, j) in arcs}
        while target is not None:
            traversed_path.insert(0, target)
            if previous_nodes[target] is not None:
                a, b = previous_nodes[target], target
                flow_tracked[(a, b)] = 1
            target = previous_nodes[target]
        return traversed_path, flow_tracked

    # Choose random source node from terminals
    src = random.choice(terminals)

    # Execute Dijkstra's from source to all terminal nodes
    min_distances, previous_nodes = perform_dijkstra(src, VERTICES, arcs, b_costs)

    # Return only distances/paths to other terminal nodes
    paths_result = {}
    flow_details = {}

    for node in terminals:
        if node != src:
            path, flow = recover_path_and_flow(previous_nodes, node, arcs)
            paths_result[node] = {'distance': min_distances[node], 'path': path}
            flow_details[node] = flow

    return flow_details

def LR2(VERTICES, EDGES, weights, costs, terminals, source, mult):
    # Create bidirectional version of edges
    arcs = EDGES + [(end, start) for (start, end) in EDGES]

    # Copy costs and add reverse edge costs
    b_costs = costs.copy()
    for (start, end) in EDGES:
        b_costs[(end, start)] = costs[(start, end)]

    # Copy edge weights for reverse edges
    b_weights = weights.copy()
    for (start, end) in EDGES:
        b_weights[(end, start)] = weights[(start, end)]

    # Initialize x for all edges in arcs
    x = {edge: 0 for edge in arcs}

    # Map weights to edges
    weight_map = {}
    for edge, color in b_weights.items():
        if color not in weight_map:
            weight_map[color] = []
        weight_map[color].append(edge)

    # Iterate through each color and choose reduced cost edges
    def algorithm_1(arcs, b_costs, mult, weight_map):
        costs_reduced = {}
        
        for color in weight_map:
            lowest_edge = None
            min_cost = float('inf')
            
            for edge in weight_map[color]:
                a, b = edge
                this_reduced_cost = b_costs[edge] - sum(mult.get((a, b, node), 0) for node in terminals if node != source)
                costs_reduced[edge] = this_reduced_cost
                
                if this_reduced_cost < min_cost:
                    min_cost = this_reduced_cost
                    lowest_edge = edge
            
            if min_cost < 0:
                x[lowest_edge] = 1
        
        return x, costs_reduced

    # Implement Algorithm 1 on the arcs
    selected_edges, reduced_costs = algorithm_1(arcs, b_costs, mult, weight_map)

    return selected_edges, weight_map

def update_x_based_on_flow(flow_details, arcs, x):
    for node, flow in flow_details.items():
        for edge, this_flow in flow.items():
            if this_flow > 0:
                x[edge] = 1

def build_subgraph(arcs, selected_edges, b_costs, b_weights):
    """
    Constructs the subgraph based on the selected edges.
    """
    nodes_set = set()
    edge_set = set()
    arcs_cost = {}
    weights_cost = {}
    
    # Go through all arcs and include only those that are selected
    for (start, end) in arcs:
        if selected_edges.get((start, end), 0) == 1:
            nodes_set.add(start)
            nodes_set.add(end)
            edge_set.add((start, end))
            arcs_cost[(start, end)] = b_costs[(start, end)]
            weights_cost[(start, end)] = b_weights[(start, end)]

    return nodes_set, arcs_cost, weights_cost, edge_set

def solve_Lagrange_Relaxtion(NODES, edge_bar, weight_bar, arcs, terminals, source):
    source = random.choice(terminals)

    # Remove source node from terminals
    remaining_terminals = [node for node in terminals if node != source]
    
    # Define directions for edges and remove duplicates
    arcs_directed = list(set(list(edge_bar) + [(end, start) for (start, end) in edge_bar]))

    # Initialize model
    model = gb.Model("Lagrangian Relaxation")
    
    # Decision variables
    x = model.addVars(edge_bar, vtype=gb.GRB.BINARY, name="x")
    f = model.addVars(arcs_directed, remaining_terminals, lb=0.0, name="f")
    
    # Objective: Minimize cost
    model.modelSense = gb.GRB.MINIMIZE
    model.setObjective(gb.quicksum(arcs[edge] * x[edge] for edge in edge_bar))
    
    # Flow conservation constraints
    for node in NODES:
        for terminal in remaining_terminals:
            model.addConstr(
                gb.quicksum(f[node, target, terminal] for target in NODES if (node, target) in arcs_directed) - 
                gb.quicksum(f[src, node, terminal] for src in NODES if (src, node) in arcs_directed) == 
                (1 if node == source else -1 if node == terminal else 0),
                name=f"flow_conservation_{node}_{terminal}"
            )
    
    # Capacity constraints
    for (start, end) in edge_bar:
        for terminal in remaining_terminals:
            model.addConstr(f[start, end, terminal] <= x[start, end], name=f"flow_capacity_{start}_{end}_{terminal}")
            model.addConstr(f[end, start, terminal] <= x[start, end], name=f"flow_capacity_{end,start}_{terminal}")
    
    # Rainbow constraints
    for color in set(weight_bar.values()):
        model.addConstr(
            gb.quicksum(x[edge] for edge in edge_bar if edge in weight_bar and weight_bar[edge] == color) <= 1,
            name=f"color_constraint_{color}"
        )
    
    # Optimize model
    model.optimize()
    
    if model.status == gb.GRB.INFEASIBLE:
        print("Model is infeasible. Diagnosing...")
        model.computeIIS()
        model.write("model.ilp")
    elif model.status == gb.GRB.OPTIMAL:
        print(f"Optimization status: {model.status}")
        print(f"Optimal obj value: {model.objVal}")
        print("Edges in solution:")
        for edge in edge_bar:
            if x[edge].x > 0.5:
                print(f"Edge {edge} with cost {arcs[edge]}")
        print("Flow values:")
        for (node_a, node_b) in arcs_directed:
            for terminal in remaining_terminals:
                if f[node_a, node_b, terminal].x > 0:
                    print(f"Flow from {node_a} to {node_b} for commodity {terminal}: {f[node_a, node_b, terminal].x}")
    else:
        print(f"Model optimization failed with status: {model.status}")

    # Ensure model objVal and other metrics are accessible
    return model

def Lagrangian_Relaxation(VERTICES, EDGES, weights, costs, terminals, source):
    mult = {}
    upper_bound = float('inf')
    remaining_terminals = [node for node in terminals if node != source]

    for node in remaining_terminals:
        for (start, end) in EDGES:
            mult[start, end, node] = costs[(start, end)]

    iter_count = 0
    max_iters = 100
    selected_edges = {edge: 0 for edge in EDGES}

    weight_map = {}
    for edge, color in weights.items():
        if color not in weight_map:
            weight_map[color] = []
        weight_map[color].append(edge)

    while iter_count <= max_iters:
        # Step 1: Execute LR1 to get flow outcomes for each terminal
        flow_details = LR1(VERTICES, EDGES, weights, costs, terminals, None)
        
        # Step 2: Use LR2 to obtain selected edges via reduced cost
        selected_edges, weight_map = LR2(VERTICES, EDGES, weights, costs, terminals, None, mult)

        # Step 3: Insert bidirectional edges
        arcs = EDGES + [(end, start) for (start, end) in EDGES]
        b_costs = costs.copy()
        b_weights = weights.copy()

        # Add associated costs and weights for reverse arcs
        for (start, end) in EDGES:
            b_costs[(end, start)] = costs[(start, end)]
            b_weights[(end, start)] = weights[(start, end)]

        # Step 4: Update x by employing flow results
        update_x_based_on_flow(flow_details, arcs, selected_edges)

        # Step 5: Compile subgraph B(N, \overline{A})
        nodes_set, arcs_cost, weights_cost, edge_set = build_subgraph(arcs, selected_edges, b_costs, b_weights)

        # Step 6: Address the Lagrangian relaxation question using the formed subgraph
        model = solve_Lagrange_Relaxtion(nodes_set, edge_set, weights_cost, arcs_cost, terminals, source)

        # Refresh the upper limit if a superior option emerges
        if model.status == gb.GRB.OPTIMAL and model.objVal < upper_bound:
            upper_bound = model.objVal

        iter_count += 1

    return upper_bound

# Implement Lagrangian relaxation
# Make sure to define necessary inputs: VERTICES, EDGES, weights, costs, terminals
# Example data
VERTICES = [1, 2, 3, 4, 5]

EDGES = [
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (1, 5),
    (2, 5)
]

weights = {
    (1, 2): 'red',
    (2, 3): 'blue',
    (3, 4): 'red',
    (4, 5): 'blue',
    (1, 5): 'green',
    (2, 5): 'green'
}

costs = {
    (1, 2): 4,
    (2, 3): 3,
    (3, 4): 5,
    (4, 5): 2,
    (1, 5): 7,
    (2, 5): 6
}

terminals = [1, 3, 5]

Lagrangian_Relaxation(VERTICES, EDGES, weights, costs, terminals, None)