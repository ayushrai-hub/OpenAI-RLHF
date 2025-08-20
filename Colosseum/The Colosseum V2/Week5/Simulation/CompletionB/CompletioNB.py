def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    DIRECTIONS = {
        (0, -1): "W",
        (0, 1): "S",
        (-1, 0): "A",
        (1, 0): "D"
    }
    
    for _ in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]
        
        lattice = Lattice.from_grid(lawn, directions=list(DIRECTIONS.keys()))

        start = next(node for node in lattice if lattice.label_dict[node] == ".")
        path = find_path(lattice, start, visited=set())

        output.append(path)

    return "\n".join(output)


def find_path(lattice: Lattice, current: Node, visited: set[Node]) -> str:
    if len(visited) == lattice.num_nodes(lambda node: lattice.label_dict[node] != "X"):
        return ""

    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        next_node = Node(current.x + dx, current.y + dy)
        if lattice.has_node(next_node) and next_node not in visited:
            if lattice.label_dict[next_node] != "X":
                visited.add(next_node)
                part_path = find_path(lattice, next_node, visited)
                if part_path is not None:
                    return DIRECTIONS[(dx, dy)] + part_path
                visited.remove(next_node)

    return None
