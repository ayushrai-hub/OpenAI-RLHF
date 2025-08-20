def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    for lawn_i in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        # Create lattice graph excluding the tree cell
        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        walkable = lattice.sublattice(only=lambda node: lattice.label_dict[node] != "X")

        # Get walkable nodes
        walkable_nodes = list(walkable)

        # Start at any free cell
        start_node = walkable_nodes[0]

        # Generate valid path using DFS
        visited: set[Node] = set()
        path: list[str] = []

        def dfs(node: Node):
            visited.add(node)

            # Explore unvisited neighbors
            for direction, (dx, dy) in zip("WDSA", DIRECTIONS):  # Directions: S, D, W, A
                neighbor = Node(node.x + dx, node.y + dy)
                if neighbor in walkable.graph.nodes and neighbor not in visited:
                    path.append(direction)
                    dfs(neighbor)
                    path.append("BACK")  # Placeholder for backtracking

        dfs(start_node)

        # Cleanup path (remove "BACK" placeholders)
        final_path = []
        for i, step in enumerate(path):
            if step == "BACK":
                if final_path:
                    final_path.pop()  # Remove the previous step (backtrack)
            else:
                final_path.append(step)

        output.append("".join(final_path))

    return "\n".join(output)


if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
