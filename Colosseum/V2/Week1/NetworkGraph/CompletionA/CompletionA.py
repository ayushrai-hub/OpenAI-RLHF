import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: List[str] = []

    graph_i = 0
    while lines:
        graph_i += 1

        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: List[List[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        walkable = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")
        
        # Find all nodes that need to be visited (all '.' cells)
        nodes_to_visit = [node for node in walkable if lattice.label_dict[node] == '.']

        # Try to find a path that visits all nodes
        path = find_path_visiting_all_nodes(walkable, nodes_to_visit)

        if path:
            path_string = translate_path_to_directions(path)
            output.append(path_string)
        else:
            output.append("INVALID")

        if plot:
            plt.figure(figsize=(10, 10))
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="lightgrey")
            if path:
                plot_path(lattice, path)
            plt.show()

    return "\n".join(output)

def find_path_visiting_all_nodes(graph: nx.Graph, nodes_to_visit: List[Point]) -> List[Point]:
    if not nodes_to_visit:
        return []
    
    start = nodes_to_visit[0]
    current_path = [start]
    remaining_nodes = set(nodes_to_visit[1:])

    while remaining_nodes:
        nearest = min(remaining_nodes, 
                      key=lambda node: nx.shortest_path_length(graph, current_path[-1], node))
        path_segment = nx.shortest_path(graph, current_path[-1], nearest)
        current_path.extend(path_segment[1:])  # Exclude the first node to avoid duplication
        remaining_nodes.remove(nearest)

    return current_path

def translate_path_to_directions(path: List[Point]) -> str:
    wasd = ""
    for i in range(1, len(path)):
        dx, dy = path[i].x - path[i-1].x, path[i].y - path[i-1].y
        if dx == 1:
            wasd += "D"
        elif dx == -1:
            wasd += "A"
        elif dy == 1:
            wasd += "S"
        elif dy == -1:
            wasd += "W"
    return wasd

def plot_path(lattice: Lattice, path: List[Point]):
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(
        lattice.graph,
        lattice.position_dict,
        nodelist=path,
        node_color="lightblue",
        node_size=500,
    )
    nx.draw_networkx_edges(
        lattice.graph,
        lattice.position_dict,
        edgelist=path_edges,
        edge_color="red",
        width=2,
    )
    nx.draw_networkx_labels(
        lattice.graph,
        lattice.position_dict,
        labels={node: lattice.label_dict[node] for node in path},
        font_size=8,
        font_weight="bold",
    )
