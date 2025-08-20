def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))  # Number of lawns
    output = []

    for graph_i in range(n):
        lawn_dimensions = tuple(map(int, lines.pop(0).split()))
        lawn_width, lawn_height = lawn_dimensions
        lawn = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]
        
        lattice = Lattice.from_grid(lawn, directions=ALL_DIRECTIONS)
        
        # Valid path finding:
        start, end = None, None
        for y in range(lawn_height):
            for x in range(lawn_width):
                if lawn[y][x] == '.':
                    if start is None:
                        start = Node(x, y)
                    end = Node(x, y)
        
        if start is None or end is None:
            output.append("INVALID")
            continue
        
        valid_path = find_valid_path(lawn, start, end)

        if valid_path is None:
            output.append("INVALID")
        else:
            output.append("".join(valid_path))
        
        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i + 1}")
            lattice.plot()
            if valid_path:
                path_pos = [node for node in valid_path]
                nx.draw_networkx_nodes(
                    lattice.graph,
                    position=lattice.position_dict,
                    nodelist=path_pos,
                    node_color="orange",
                )
                plt.show()

    return "\n".join(output)

def find_valid_path(lawn: list[list[str]], start: Node, end: Node) -> list[Node] | None:
    """Attempts to find a valid path through the lawn from start to end."""
    def is_within_bounds(node: Node) -> bool:
        return 0 <= node.x < len(lawn[0]) and 0 <= node.y < len(lawn)

    directions = {
        'W': (-1, 0),
        'D': (0, 1),
        'S': (1, 0),
        'A': (0, -1),
    }

    from collections import deque
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        for direction, (dx, dy) in directions.items():
            next_node = Node(current.x + dx, current.y + dy)
            if not is_within_bounds(next_node):
                continue
            if lawn[next_node.y][next_node.x] == 'X':
                continue
            if next_node in path:
                continue

            next_path = path + [next_node]
            if next_node == end:
                return next_path
            queue.append((next_node, next_path))

    return None

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=None, test=False, plot_all=False)
