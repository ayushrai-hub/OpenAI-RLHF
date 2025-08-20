def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    # Directions and their mapping to move chars
    directions = {
        (0, -1): 'W',
        (1, 0): 'D',
        (0, 1): 'S',
        (-1, 0): 'A',
    }
    moves = [(0,-1),(1,0),(0,1),(-1,0)]  # Up, Right, Down, Left order (can be changed)

    for _ in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        # Find all free cells and the tree cell
        free_cells = [(x,y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == '.']
        tree_cell = [(x,y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == 'X'][0]

        # We'll pick the top-leftmost free cell as start (or any free cell)
        start = free_cells[0]

        visited = set()
        path_cells: list[tuple[int,int]] = []

        def backtrack(cx: int, cy: int) -> bool:
            path_cells.append((cx, cy))
            visited.add((cx, cy))

            if len(visited) == len(free_cells):
                return True

            for (dx, dy) in moves:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < lawn_width and 0 <= ny < lawn_height:
                    if (nx, ny) not in visited and lawn[ny][nx] == '.':
                        if backtrack(nx, ny):
                            return True

            # backtrack
            visited.remove((cx, cy))
            path_cells.pop()
            return False

        backtrack(*start)

        # Convert cell path to direction string
        path_str_chars: list[str] = []
        for i in range(1, len(path_cells)):
            x1,y1 = path_cells[i-1]
            x2,y2 = path_cells[i]
            dx, dy = (x2 - x1, y2 - y1)
            path_str_chars.append(directions[(dx, dy)])

        output.append(''.join(path_str_chars))

    return "\n".join(output)


if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
