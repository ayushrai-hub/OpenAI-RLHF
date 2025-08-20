def validate_path(lattice: Lattice, start: Point, directions: str) -> bool:
    visited = set()
    current = start
    visited.add(current)

    moves = {'W': (0, -1), 'A': (-1, 0), 'S': (0, 1), 'D': (1, 0)}

    for direction in directions:
        dx, dy = moves.get(direction, (0, 0))
        next_point = Point(current.x + dx, current.y + dy)

        if (
          next_point in visited or
          not (0 <= next_point.x < lattice.width) or
          not (0 <= next_point.y < lattice.height) or
          lattice.grid[next_point.y][next_point.x] == 'X'
        ):
            return False

        visited.add(next_point)
        current = next_point

    # Check if all free cells were visited
    total_free_cells = sum(row.count('.') for row in lattice.grid)
    return len(visited) == total_free_cells
def get_shortest_path(lattice: Lattice, source: Point, target: Point):
    try:
        path = lattice.shortest_path(source=source, target=target)
        directions = translate_path_to_directions(list(path))
        return directions
    except nx.NetworkXNoPath:
        return None

def translate_path_to_directions(path: list[Point]) -> str:
    moves = { (0, -1): 'W', (-1, 0): 'A', (0, 1): 'S', (1, 0): 'D' }
    directions = ''
    for prev, current in zip(path, path[1:]):
        direction = (current.x - prev.x, current.y - prev.y)
        directions += moves[direction]
    return directions
