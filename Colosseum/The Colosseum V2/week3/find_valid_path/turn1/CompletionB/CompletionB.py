def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))  # number of lawns
    output: list[str] = []

    # Direction vectors: (dx, dy, direction_char)
    moves = [
        (1, 0, 'D'),
        (-1, 0, 'A'),
        (0, 1, 'S'),
        (0, -1, 'W'),
    ]

    for _ in range(n):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(line) for line in lines[:lawn_height]]
        lines = lines[lawn_height:]

        # Collect all free cells
        free_cells = [(x, y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == '.']

        # We need to find a path that covers all free cells
        # Let’s pick the first free cell as a start:
        start = free_cells[0]

        visited = set()
        visited.add(start)
        path_nodes = [start]

        def backtrack(current: tuple[int, int]) -> bool:
            if len(visited) == len(free_cells):
                return True  # found path

            for dx, dy, _ in moves:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < lawn_width and 0 <= ny < lawn_height:
                    if lawn[ny][nx] == '.' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        path_nodes.append((nx, ny))
                        if backtrack((nx, ny)):
                            return True
                        visited.remove((nx, ny))
                        path_nodes.pop()

            return False

        backtrack(start)

        # Convert path_nodes to direction string
        path_str = []
        for i in range(len(path_nodes) - 1):
            x1, y1 = path_nodes[i]
            x2, y2 = path_nodes[i + 1]
            dx, dy = x2 - x1, y2 - y1

            if dx == 1 and dy == 0:
                path_str.append('D')
            elif dx == -1 and dy == 0:
                path_str.append('A')
            elif dx == 0 and dy == 1:
                path_str.append('S')
            elif dx == 0 and dy == -1:
                path_str.append('W')

        output.append("".join(path_str))

    return "\n".join(output)


if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
