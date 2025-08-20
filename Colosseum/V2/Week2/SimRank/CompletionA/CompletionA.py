def simrank(G, r=0.9, max_iter=10, eps=1e-4):
    nodes = G.nodes()
    sim = { (u,v): 1.0 if u == v else 0.0 for u in nodes for v in nodes }
    for iter_ctr in range(max_iter):
        prev_sim = sim.copy()
        for u in nodes:
            for v in nodes:
                if u == v:
                    continue
                neighbors_u = list(G.predecessors(u))
                neighbors_v = list(G.predecessors(v))
                if not neighbors_u or not neighbors_v:
                    sim[(u,v)] = 0.0
                else:
                    s = sum(prev_sim[(n_u, n_v)] for n_u in neighbors_u for n_v in neighbors_v)
                    sim[(u,v)] = (r * s) / (len(neighbors_u) * len(neighbors_v))
        # Check convergence
        if max(abs(sim[(u,v)] - prev_sim[(u,v)]) for u in nodes for v in nodes) < eps:
            break
    return sim


import networkx as nx

def extended_jaccard_coefficient(G, u, v, radius=2):
    def get_extended_neighbors(node):
        return set(nx.single_source_shortest_path_length(G, node, cutoff=radius).keys())
    
    neighbors_u = get_extended_neighbors(u)
    neighbors_v = get_extended_neighbors(v)
    
    intersection = neighbors_u.intersection(neighbors_v)
    union = neighbors_u.union(neighbors_v)
    
    if not union:
        return 0.0
    return len(intersection) / len(union)

# Example usage
G = nx.Graph()
# Add edges to G
similarity = extended_jaccard_coefficient(G, 'node1', 'node2')
print(similarity)
