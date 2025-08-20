def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))  # Number of lawns

    output: list[str] = []

    for _ in range(n):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        lattice = Lattice.from_grid(lawn, directions=None)

        path = solve_lawn(lattice, lawn_width, lawn_height)
        output.append(path)

    return "\n".join(output)


def solve_lawn(lattice: Lattice, lawn_width: int, lawn_height: int) -> str:
    # Find all free cells
    free_cells = [node for node in lattice if lattice.label_dict[node] == '.']

    # Start from an edge cell (the edges are guaranteed to be free cells).
    edge_cells = [node for node in free_cells if node.x in [0, lawn_width - 1] or node.y in [0, lawn_height - 1]]
    start_node = edge_cells[0]

    visited = set()
    path_nodes = []

    def backtrack(node: Node) -> bool:
        visited.add(node)
        path_nodes.append(node)

        if len(visited) == len(free_cells):
            return True  # All free cells visited

        # Define neighbor offsets (N, E, S, W)
        directions = [(-1,0),(0,1),(1,0),(0,-1)]
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            next_node = Node(nx, ny)
            if 0 <= nx < lawn_width and 0 <= ny < lawn_height:
                if next_node in free_cells and next_node not in visited:
                    if backtrack(next_node):
                        return True

        visited.remove(node)
        path_nodes.pop()
        return False

    backtrack(start_node)

    # Convert path_nodes to directions
    if not path_nodes:
        return ""  # No path found, though guaranteed by problem statement

    directions_str = []
    for i in range(len(path_nodes) - 1):
        current = path_nodes[i]
        next_ = path_nodes[i + 1]
        if next_.y == current.y - 1:  # Moved Up (North)
            directions_str.append('W')
        elif next_.y == current.y + 1:  # Moved Down (South)
            directions_str.append('S')
        elif next_.x == current.x + 1:  # Moved Right (East)
            directions_str.append('D')
        elif next_.x == current.x - 1:  # Moved Left (West)
            directions_str.append('A')

    return "".join(directions_str)


if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=None, test=False, plot_all=False)
