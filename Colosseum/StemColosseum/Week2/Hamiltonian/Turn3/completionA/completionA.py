def find_hamiltonian_path(graph: nx.Graph, start_node: Node) -> list[Node] | None:
    def backtrack(current_path: list[Node], visited: set[Node]) -> list[Node] | None:
        if len(current_path) == len(graph):
            return current_path
        
        current_node = current_path[-1]
        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                result = backtrack(current_path + [neighbor], visited)
                if result:
                    return result
                visited.remove(neighbor)
        return None

    return backtrack([start_node], {start_node})

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
        
        # Start from any walkable node
        start_node = next(iter(walkable.nodes))
        path = find_hamiltonian_path(walkable, start_node)

        if not path:
            raise ValueError("No Hamiltonian path found, which should be impossible according to the problem description.")
        
        path_string = translate_path_to_directions(path)

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            nx.draw(
                walkable, pos={node: (node.x, node.y) for node in path},
                labels={node: lattice.label_dict[node] for node in path}, with_labels=True, node_color="blue"
            )
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
