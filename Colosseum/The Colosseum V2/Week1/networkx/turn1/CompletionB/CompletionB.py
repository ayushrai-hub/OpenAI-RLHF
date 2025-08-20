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
        walkable_nodes = [node for node in lattice.graph.nodes if lattice.label_dict[node] != "X"]

        # Convert the nodes to their coordinates
        node_positions = {node: (node.x, node.y) for node in walkable_nodes}

        # Build subgraph for non-tree nodes
        walkable_subgraph = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")
        
        # Find Hamiltonian Path
        try:
            hamiltonian_path = nx.algorithms.tournamental.hamiltonian_path(walkable_subgraph)
        except nx.NetworkXError:
            # If not strong connected, handle accordingly (return invalid or empty)
            output.append("INVALID")
            continue

        path_string = translate_path_to_directions(hamiltonian_path)

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            pos = {node: (node.x, node.y) for node in lattice.graph.nodes}
            nx.draw(
                lattice.graph, pos=pos,
                labels={node: lattice.label_dict[node] for node in lattice.graph.nodes}, with_labels=True, node_color="blue"
            )
            plt.plot([pos[node][0] for node in hamiltonian_path],
                     [pos[node][1] for node in hamiltonian_path], color='red')
            plt.show()

        output.append(path_string)

    return "\n".join(output)

def translate_path_to_directions(path: list[Node]) -> str:
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
