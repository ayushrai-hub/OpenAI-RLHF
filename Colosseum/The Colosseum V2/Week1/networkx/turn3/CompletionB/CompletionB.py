def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    for graph_i, lines_chunk in enumerate(split_lines(lines), start=1):
        lawn_width, lawn_height = tuple(map(int, lines_chunk[0].split()))
        lawn = [list(line) for line in lines_chunk[1:1+lawn_height]]
        path_string = lines_chunk[1+lawn_height]
        
        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        graph = lattice.subgraph(only=lambda node: lattice.label_dict[node] != "X")
        
        try:
            hamiltonian_nodes = nv.hamiltonian_path(graph)
        except nx.NetworkXError:
            output.append('INVALID')
            continue
        
        if not hamiltonian_nodes:
            output.append('INVALID')
            continue
        
        # Ensure the whole path is within the dimensions of the lawn
        hamiltonian_nodes = [node for node in hamiltonian_nodes
                              if 0 <= node[0] < lawn_width and 0 <= node[1] < lawn_height]
        if len(hamiltonian_nodes) == 1 and lattice.label_dict[hamiltonian_nodes[0]] == 'X':
            output.append('INVALID')
            continue
        
        path = translate_path_to_directions(hamiltonian_nodes)
        output.append(path)

        if plot and path != 'INVALID':
            plot_path(lattice, path, graph_i)

    return '\n'.join(output)


def plot_path(lattice, path, graph_i):
    plt.gca().invert_yaxis()
    plt.title(f"Graph {graph_i}")
    lattice.plot(node_color="green")
    nx.shortest_path_path = None
    pr = nx.all_pairs_shortest_path_length(lattice.graph, weight=model)
    # iterate over the edges of path
    edges = path_edges(lattice.graph, path[0])
    for src, dst in edges:
        labels = calculate_labels(pr, src, dst)
        nx.draw(
            lattice.graph, with_labels=True, node_color="green", labels=labels
        )
        plt.show()


def path_edges(graph, path):
    return zip(path[:-1], path[1:])


def translate_path_to_directions(hamiltonian_nodes):
    wasd = ""
    for i in range(1, len(hamiltonian_nodes)):
        dx, dy = hamiltonian_nodes[i][0] - hamiltonian_nodes[i - 1][0], hamiltonian_nodes[i][1] - hamiltonian_nodes[i - 1][1]
        wasd += {(-1, 0): 'A', (1, 0): 'D', (0, -1): 'W', (0, 1): 'S'}.get((dx, dy), '')
    return wasd
