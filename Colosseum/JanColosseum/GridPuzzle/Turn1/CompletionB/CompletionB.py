DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # W, D, S, A mapping

DIRECTION_TO_CHAR = {
    (0, -1): "W",  # Up
    (1, 0): "D",   # Right
    (0, 1): "S",   # Down
    (-1, 0): "A"   # Left
}

def find_start(lawn: list[list[str]]) -> tuple[int, int]:
    """Find any starting point in the lawn that is not a tree."""
    for y, row in enumerate(lawn):
        for x, cell in enumerate(row):
            if cell == '.':
                return x, y
    return -1, -1  # Should not happen as there's always at least one valid path

def generate_path(lawn: list[list[str]], start: tuple[int, int]) -> str:
    """Generate a valid zigzag path for the lawn starting at `start`."""
    height = len(lawn)
    width = len(lawn[0])
    x, y = start
    visited = set()
    path = []
    for y in range(height):
        rows = range(width) if y % 2 == 0 else range(width - 1, -1, -1)
        for x in rows:
            if lawn[y][x] == '.':  # Only walk on free cells
                if visited:
                    dx, dy = x - prev_x, y - prev_y
                    path.append(DIRECTION_TO_CHAR[(dx, dy)])
                visited.add((x, y))
                prev_x, prev_y = x, y
    return ''.join(path)

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    for _ in range(n):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0)) for _ in range(lawn_height)]
        
        # Use the tree-avoiding logic for finding a start point and generating a path
        start = find_start(lawn)
        path = generate_path(lawn, start)

        # Validate path if needed
        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        if not lattice.has_node(Node(*start)):
            output.append("INVALID")
        elif plot:
            lattice.plot(plot)
            print(f"Generated path: {path}")
            
        output.append(path)

    return "\n".join(output)

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
