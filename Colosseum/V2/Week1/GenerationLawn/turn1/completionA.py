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
        walkable = lattice.sublattice(only=lambda node: lattice.label_dict[node] != "X")

        possible_paths = []

        for start_x in range(lawn_width):
            for start_y in range(lawn_height):
                if lawn[start_y][start_x] == "X":
                    continue  # Skip if the tree

                for end_x in range(lawn_width):
                    for end_y in range(lawn_height):
                        if lawn[end_y][end_x] == "X" or (start_x == end_x and start_y == end_y):
                            continue  # Skip if tree or same spot

                        path_graph = build_path_graph_from_start_end(lawn, (start_x, start_y), (end_x, end_y))

                        # Ensure the nodes in path are within the bounds and valid within the lattice
                        if (
                            path_graph.number_of_nodes() == walkable.num_nodes
                            and all(lattice.has_node(Node(x, y)) and lattice.label_dict[Node(x, y)] != "X" for x, y in path_graph.nodes)
                            and all(0 <= x < lawn_width and 0 <= y < lawn_height for x, y in path_graph.nodes)
                        ):
                            possible_paths.append("".join(get_path_representation(path_graph)))
        
        # Return or store multiple valid paths for the lawn
        output.append("\n".join(possible_paths) if possible_paths else "INVALID")

    return "\n".join(output)

# Assuming build_path_graph_from_start_end and get_path_representation are implemented
# Implementations of these helper functions would depend on the specifics of how we're interpreting valid paths.
