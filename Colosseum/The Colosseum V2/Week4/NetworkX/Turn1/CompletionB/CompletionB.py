import networkx as nx

# Create your grid graph G with adjacency from your layout
# For example:
# G = nx.Graph()
# add edges between adjacent free cells

# Then, to find the shortest path (fewest edges) from node A to node B
path = nx.shortest_path(G, source=A, target=B, method='breadth_first_search')
