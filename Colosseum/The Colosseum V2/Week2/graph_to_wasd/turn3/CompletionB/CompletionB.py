import networkx as nx

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
        nodes_set = set(lattice.graph.nodes)
        
        if len(nodes_set) < 4:  # need at minimum 4 non-tree nodes for Hamiltonian path
            output.append("")
            continue
        
        hamiltonian_path = None
        if nx.is_directed_acyclic_graph(walkable):
            try:
                hamiltonian_path = nx.hamiltonian_path(walkable)
            except nx.NetworkXError:
                pass
        
        if not hamiltonian_path:
            output.append("INFEASIBLE")
            continue
        
        path_string = translate_path_to_directions(list(hamiltonian_path))
        
        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            path_nodes = list(hamiltonian_path)
            nx.draw(
                walkable, pos={node: node for node in path_nodes},
                labels={node: lattice.label_dict[node] for node in path_nodes}, with_labels=True, node_color="blue"
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
