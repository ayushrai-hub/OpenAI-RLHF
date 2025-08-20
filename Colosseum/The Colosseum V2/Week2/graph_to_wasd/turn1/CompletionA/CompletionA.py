import networkx as nx
from networkx.algorithms.tournament import is_tournament

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    graph_i = 0
    while lines:
        graph_i += 1

        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)

        # Convert lattice to a directed graph (treating it as a tournament)
        lattice_directed = lattice.graph.to_directed()

        # Ensure the graph is a tournament before calling nx.hamiltonian_path
        if not is_tournament(lattice_directed):
            raise ValueError("Lattice graph is not a tournament; cannot find Hamiltonian path.")

        path_nodes = nx.hamiltonian_path(lattice_directed)

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            path_graph = nx.path_graph(path_nodes)  # Or edges as required in the plot
            nx.draw(
                path_graph, pos={node: node for node in path_nodes},
                labels={node: lattice.label_dict[node] for node in path_nodes}, with_labels=True, node_color="blue"
            )
            plt.show()

        path_string = graph_to_wasd(path_nodes)

        output.append(path_string)

    return "\n".join(output)


def graph_to_wasd(path_nodes: list[Node]) -> str:
    wasd = ""
    for i in range(1, len(path_nodes)):
        dx, dy = path_nodes[i].x - path_nodes[i-1].x, path_nodes[i].y - path_nodes[i-1].y
        if dx == 1:
            wasd += "D"
        elif dx == -1:
            wasd += "A"
        elif dy == 1:
            wasd += "S"
        elif dy == -1:
            wasd += "W"
    return wasd
