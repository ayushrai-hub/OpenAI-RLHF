# Path 1-2-3 (shortest path between cells)
nx.shortest_path(graph, source=(0,0), target=(2,2))

visited_nodes = set(path)
required_nodes = {node for node in graph if graph.label_dict[node] != 'X'}
assert visited_nodes == required_nodes
for i in range(1, len(path)):
    assert path[i] in graph.neighbors(path[i-1])
