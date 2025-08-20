def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    for graph_i in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)

        walkable_nodes = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")
        nodes = list(walkable_nodes.nodes)

        try:
            hamiltonian_path = nx.hamiltonian_path(walkable_nodes)

            path_string = translate_path_to_directions(hamiltonian_path)

            if plot:
                plt.gca().invert_yaxis()
                plt.title(f"Graph {graph_i + 1}")
                lattice.plot(node_color="green")
                nx.draw(
                    walkable_nodes, pos={node: node for node in walkable_nodes.nodes},
                    labels={node: lattice.label_dict[node] for node in walkable_nodes.nodes}, with_labels=True, node_color="blue"
                )
                plt.show()

            output.append(path_string)
        except nx.exception.NetworkXError:
            # In case no Hamiltonian path exists (should generally not happen in well-connected graphs)
            output.append("No Hamiltonian Path found")

    return "\n".join(output)

def translate_path_to_directions(path: list[Node]) -> str:
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
