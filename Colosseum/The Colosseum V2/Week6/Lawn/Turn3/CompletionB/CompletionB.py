import networkx as nx
import matplotlib.pyplot as plt

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    graph_i = 0
    while lines:
        graph_i += 1
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn)
        
        # Create a subgraph excluding blocked (X) nodes
        valid_graph = lattice.subgraph(lambda node: lattice.label_dict[node] != 'X')

        # Choose any valid starting node
        start_node = next(node for node in valid_graph.nodes if lattice.label_dict[node] == '.')

        # Get paths to visit all nodes
        path = []
        current_node = start_node
        visited_nodes = {current_node}
        while len(visited_nodes) < len(valid_graph.nodes):
            paths = nx.single_source_shortest_path(valid_graph, current_node)
            next_node = None
            min_path_length = float('inf')
            for node, p in paths.items():
                if node not in visited_nodes and (path_len := len(p)) < min_path_length:
                    next_node = node
                    min_path_length = path_len
            if next_node is None:
                break  # no more reachable nodes
            path.extend(paths[next_node][1:])  # extend path without repeating current node
            visited_nodes.update(paths[next_node])
            current_node = next_node
        
        path_string = translate_path_to_directions(path)

        if plot:
            plt.figure(graph_i)
            lattice.plot(node_color="green")
            plt.title(f"Lawn {graph_i} Path")
            nx.draw_networkx_nodes(lattice.graph, lattice.position_dict, nodelist=path, node_color="red")
            plt.gca().invert_yaxis()
            plt.show()

        output.append(path_string)

    return "\n".join(output)


def translate_path_to_directions(path: list[Point]) -> str:
    directions = ""
    for i in range(1, len(path)):
        dx, dy = path[i].x - path[i-1].x, path[i].y - path[i-1].y
        if dx == 1:
            directions += "D"
        elif dx == -1:
            directions += "A"
        elif dy == 1:
            directions += "S"
        elif dy == -1:
            directions += "W"
    return directions

