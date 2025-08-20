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
        walkable = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")

        # Find the start node
        start_node = next((node for node in walkable if lattice.label_dict[node] == '.'), None)

        # Find the Hamiltonian Path
        if nx.is_strongly_connected(walkable):
            hamiltonian = nx.hamiltonian_path(walkable)
            path = list(hamiltonian)
        else:
            # In case the graph is not strongly connected, we fallback to manual traversal or heuristics
            path = list(nx.dfs_preorder_nodes(walkable, source=start_node))

        # Translate the path to WASD movements
        path_string = translate_path_to_directions(path)

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            nx.draw(
                walkable, pos={node: (node.x, node.y) for node in walkable.nodes()},
                labels={node: lattice.label_dict[node] for node in walkable.nodes()}, with_labels=True, node_color="blue"
            )
            plt.show()

        output.append(path_string)

    return "\n".join(output)

def translate_path_to_directions(path: list[Node]) -> str:
    wasd = ""
    for i in range(1, len(path)):
        dx = path[i].x - path[i-1].x
        dy = path[i].y - path[i-1].y
        if dx == 1:
            wasd += "D"
        elif dx == -1:
            wasd += "A"
        elif dy == 1:
            wasd += "S"
        elif dy == -1:
            wasd += "W"
    return wasd
