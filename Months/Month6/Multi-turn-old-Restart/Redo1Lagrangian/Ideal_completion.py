# ideal_completion.py
 
import heapq
import random
import gurobipy as gb

def LR1(VERTICES, EDGES, weights, costs, terminals, source):
    arcs = EDGES + [(end, start) for (start, end) in EDGES]
    b_costs = costs.copy()
    for (start, end) in EDGES:
        b_costs[(end, start)] = costs[(start, end)]

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



    def recover_path_and_flow(previous_nodes, target, arcs):
        traversed_path = []
        flow_tracked = {(i, j): 0 for (i, j) in arcs}
        current = target
        while current is not None:
            traversed_path.insert(0, current)
            if previous_nodes[current] is not None:
                a, b = previous_nodes[current], current
                flow_tracked[(a, b)] = 1
            current = previous_nodes[current]
        return traversed_path, flow_tracked

    src = random.choice(terminals)

    min_distances, previous_nodes = perform_dijkstra(src, VERTICES, arcs, b_costs)

    paths_result = {}
    flow_details = {}

    for node in terminals:
        if node != src:
            path, flow = recover_path_and_flow(previous_nodes, node, arcs)
            paths_result[node] = {'distance': min_distances[node], 'path': path}
            flow_details[node] = flow

    return flow_details

def LR2(VERTICES, EDGES, weights, costs, terminals, source, mult, weight_map):
    arcs = EDGES + [(end, start) for (start, end) in EDGES]

    b_costs = costs.copy()
    for (start, end) in EDGES:
        b_costs[(end, start)] = costs[(start, end)]

    b_weights = weights.copy()
    for (start, end) in EDGES:
        b_weights[(end, start)] = weights[(start, end)]

    x = {edge: 0 for edge in arcs}

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

    selected_edges, reduced_costs = algorithm_1(arcs, b_costs, mult, weight_map)

    return selected_edges

def update_x_based_on_flow(flow_details, arcs, x):
    for node, flow in flow_details.items():
        for edge, this_flow in flow.items():
            if this_flow > 0:
                x[edge] = 1

def solve_Lagrange_Relaxtion(NODES, edge_bar, weight_bar, arcs, terminals, source):
    source = random.choice(terminals)
    remaining_terminals = [node for node in terminals if node != source]
    arcs_directed = edge_bar + [(end, start) for (start, end) in edge_bar]
    model = gb.Model("Lagrangian Relaxation")
    x = model.addVars(edge_bar, vtype=gb.GRB.BINARY, name="x")
    f = model.addVars(arcs_directed, remaining_terminals, lb=0.0, name="f")
    model.modelSense = gb.GRB.MINIMIZE
    model.setObjective(gb.quicksum(arcs[edge] * x[edge] for edge in edge_bar))

    for node in NODES:
        for terminal in remaining_terminals:
            model.addConstr(
                gb.quicksum(f[node, target, terminal] for target in NODES if (node, target) in arcs_directed) -
                gb.quicksum(f[src, node, terminal] for src in NODES if (src, node) in arcs_directed) ==
                (1 if node == source else -1 if node == terminal else 0),
                name=f"flow_conservation_{node}_{terminal}"
            )

    for (start, end) in edge_bar:
        for terminal in remaining_terminals:
            model.addConstr(f[start, end, terminal] <= x[start, end], name=f"flow_capacity_{start}_{end}_{terminal}")
            model.addConstr(f[end, start, terminal] <= x[start, end], name=f"flow_capacity_{end}_{start}_{terminal}")

    for color in set(weight_bar.values()):
        model.addConstr(
            gb.quicksum(x[edge] for edge in edge_bar if edge in weight_bar and weight_bar[edge] == color) <= 1,
            name=f"color_constraint_{color}"
        )

    model.optimize()

    return model

def Lagrangian_Relaxation(VERTICES, EDGES, weights, costs, terminals, source):

    # Input validation
    if not VERTICES or not EDGES or not terminals:
        raise ValueError("Empty input sequences are not allowed")

    # Check if graph is connected
    def is_connected(vertices, edges):
        if not vertices:
            return True
        visited = set()
        stack = [vertices[0]]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                for edge in edges:
                    if edge[0] == vertex and edge[1] not in visited:
                        stack.append(edge[1])
                    elif edge[1] == vertex and edge[0] not in visited:
                        stack.append(edge[0])
        return len(visited) == len(vertices)

    if not is_connected(VERTICES, EDGES):
        raise ValueError("Graph must be connected")
    mult = {}
    upper_bound = float('inf')
    remaining_terminals = [node for node in terminals if node != source]

    for node in remaining_terminals:
        for (start, end) in EDGES:
            mult[start, end, node] = costs[(start, end)]

    iter_count = 0
    max_iters = 100
    selected_edges = {edge: 0 for edge in EDGES}

    b_costs = costs.copy()
    b_weights = weights.copy()

    # Add reverse edges to b_costs and b_weights
    arcs = EDGES + [(end, start) for (start, end) in EDGES]
    for (start, end) in EDGES:
        b_costs[(end, start)] = costs[(start, end)]
        b_weights[(end, start)] = weights[(start, end)]

    # Create weight_map from b_weights
    weight_map = {}
    for edge, color in b_weights.items():
        if color not in weight_map:
            weight_map[color] = []
        weight_map[color].append(edge)

    while iter_count <= max_iters:
        flow_details = LR1(VERTICES, EDGES, weights, costs, terminals, None)
        selected_edges = LR2(VERTICES, EDGES, weights, costs, terminals, None, mult, weight_map)
        update_x_based_on_flow(flow_details, arcs, selected_edges)

        def build_subgraph(arcs, x, b_costs, b_weights):
            nodes_set = set()
            arcs_cost = {}
            weights_cost = {}
            edge_set = set()

            for (a, b) in arcs:
                if x.get((a, b), 0) == 1:
                    nodes_set.add(a)
                    nodes_set.add(b)
                    norm_edge = (min(a, b), max(a, b))
                    if norm_edge not in arcs_cost:
                        arcs_cost[norm_edge] = b_costs.get((a, b), 0)
                        weights_cost[norm_edge] = b_weights.get((a, b), None)
                        edge_set.add(norm_edge)

            return list(nodes_set), arcs_cost, weights_cost, list(edge_set)

        nodes_set, arcs_cost, weights_cost, edge_set = build_subgraph(arcs, selected_edges, b_costs, b_weights)
        model = solve_Lagrange_Relaxtion(nodes_set, edge_set, weights_cost, arcs_cost, terminals, source)

        if model.status == gb.GRB.OPTIMAL:
            if model.ObjVal < upper_bound:
                upper_bound = model.ObjVal
        else:
            raise RuntimeError(f"Optimization failed with status: {model.status}")


        mult_new = {}

        for node in remaining_terminals:
            for (start, end) in edge_set:
                if (start, end) in arcs_cost and selected_edges.get((start, end), 0) == 1:
                    edges_m = {edge for edge in weight_map.get(weights_cost.get((start, end), None), []) if selected_edges.get(edge, 0) == 0}
                    if edges_m:
                        edge_m = min(edges_m, key=lambda edge: arcs_cost.get(edge, float('inf')))
                        min_edge_value = arcs_cost.get(edge_m, 0)
                        delta_mult = min_edge_value - (costs.get((start, end), 0) - sum(mult.get((start, end, node), 0) for node in remaining_terminals))
                        sigma_ek = delta_mult / len(remaining_terminals)
                        mult_new[(start, end, node)] = max(mult.get((start, end, node), 0) - sigma_ek, 0)

        mult = mult_new
        iter_count += 1

    return upper_bound

# Sample data for testing
# Define VERTICES, EDGES, weights, costs, terminals as needed before calling Lagrangian_Relaxation
# For example:
VERTICES = [1, 2, 3, 4]
EDGES = [(1, 2), (2, 3), (3, 4), (4, 1)]
weights = {(1, 2): 'red', (2, 3): 'blue', (3, 4): 'green', (4, 1): 'yellow'}
costs = {(1, 2): 1, (2, 3): 1, (3, 4): 1, (4, 1): 1}
terminals = [1, 3]
source = None

# Execute Lagrangian relaxation
Lagrangian_Relaxation(VERTICES, EDGES, weights, costs, terminals, source)