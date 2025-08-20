def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    for graph_i in range(1, n + 1):
        # Parse lawn size
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn: list[list[str]] = [list(lines.pop(0)) for _ in range(lawn_height)]

        # Parse the path
        path = lines.pop(0)

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        path_graph = build_path_graph(path)

        # Shift path graph into positive coordinates
        min_x, min_y = min(path_graph.nodes, key=lambda node: node[0])[0], min(path_graph.nodes, key=lambda node: node[1])[1]
        shifted_graph = nx.relabel_nodes(path_graph, {node: (node[0] - min_x, node[1] - min_y) for node in path_graph.nodes})

        walkable = lattice.sublattice(only=lambda node: lattice.label_dict[node] != "X")

        # Plotting if needed
        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            walkable.plot(node_color="green")
            nx.draw(shifted_graph, pos={node: node for node in shifted_graph.nodes}, with_labels=True, node_color="blue")
            plt.show()

        # Validation checks
        if shifted_graph.number_of_nodes() != walkable.num_nodes:
            output.append("INVALID")
            continue

        if any(shifted_graph.degree[node] > 2 or not lattice.has_node(node) or lattice.label_dict[node] == "X" for node in shifted_graph.nodes):
            output.append("INVALID")
            continue

        if any(
            node[0] < 0 or node[1] < 0 or node[0] >= lawn_width or node[1] >= lawn_height
            for node in shifted_graph.nodes
        ):
            output.append("INVALID")
            continue

        output.append(path)

    return "\n".join(output)

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
