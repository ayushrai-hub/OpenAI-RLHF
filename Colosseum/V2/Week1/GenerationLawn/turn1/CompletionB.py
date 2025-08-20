def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    for graph_i in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]
        
        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        
        # Find start and end points that are not 'X'
        start, end = None, None
        for y in range(lawn_height):
            for x in range(lawn_width):
                if lawn[y][x] != 'X':
                    if not start:
                        start = Node(x, y)
                    end = Node(x, y)
        
        # Find a valid path
        path = find_valid_path(lattice, start, end)
        
        if path:
            output.append("".join(path))
        else:
            output.append("INVALID")

    return "\n".join(output)

def find_valid_path(lattice: Lattice, start: Node, end: Node) -> list[str] | None:
    # Implementation of an algorithm to find a valid path in the lattice
    # This could be BFS, DFS, or other suitable methods to explore nodes
    # You need to explore valid paths that meet the criteria of "valid path"
    directions = {
        'W': (-1, 0),
        'D': (0, 1),
        'S': (1, 0),
        'A': (0, -1)
    }
    
    stack: list[tuple[Node, list[Node], str]] = [(start, [start], "")]
    visited = set()
    
    while stack:
        current_node, path, path_string = stack.pop()
        
        if current_node == end and len(path) == lattice.num_nodes:
            return list(path_string)
        
        for direction, (dx, dy) in directions.items():
            new_node = Node(current_node.x + dx, current_node.y + dy)
            if lattice.has_node(new_node) and new_node not in visited and lattice.label_dict[new_node] != 'X':
                stack.append((new_node, path + [new_node], path_string + direction))
                visited.add(new_node)
    
    return None

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
