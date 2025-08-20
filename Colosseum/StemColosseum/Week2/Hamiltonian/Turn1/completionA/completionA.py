def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    graph_i = 0
    for lawn_index in range(n):
        graph_i += 1

        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        walkable_nodes = [node for node in lattice if lattice.label_dict[node] != "X"]

        walkable = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")

        # Start from any free cell
        start_node = walkable_nodes[0]

        # Use backtracking to find Hamiltonian path
        path = find_hamiltonian_path(walkable, start_node)

        if path is None:
            # Should not happen as per problem statement
            output.append("NO VALID PATH")
            continue

        path_string = translate_path_to_directions(path)

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Lawn {graph_i}")
            lattice.plot(node_color="green")
            nx.draw(
                walkable, pos={node: (node.x, node.y) for node in walkable.nodes()},
                labels={node: lattice.label_dict[node] for node in walkable.nodes()},
                with_labels=True, node_color="blue",
            )
            nx.draw_networkx_edges(
                walkable, pos={node: (node.x, node.y) for node in walkable.nodes()},
                edgelist=list(zip(path[:-1], path[1:])), edge_color="red",
            )
            plt.show()

        output.append(path_string)

    return "\n".join(output)

def find_hamiltonian_path(graph: nx.Graph, start_node: Node) -> list[Node] | None:
    total_nodes = graph.number_of_nodes()
    path = [start_node]
    visited = set(path)

    def dfs(current_node):
        if len(path) == total_nodes:
            return True  # Found a Hamiltonian path
        for neighbor in sorted(graph.neighbors(current_node), key=lambda n: graph.degree[n]):
            if neighbor not in visited:
                path.append(neighbor)
                visited.add(neighbor)
                if dfs(neighbor):
                    return True
                path.pop()
                visited.remove(neighbor)
        return False

    if dfs(start_node):
        return path
    else:
        return None  # No Hamiltonian path found

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
