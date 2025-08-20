def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().split('\n')
    N = int(lines.pop(0))

    output = []

    for lawn_index in range(N):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn_grid = [list(lines.pop(0).strip()) for _ in range(lawn_height)]

        path = find_valid_path(lawn_grid)

        if path is None:
            output.append('NO SOLUTION')
        else:
            output.append(''.join(path))

    return '\n'.join(output)


def find_valid_path(grid):
    width, height = len(grid[0]), len(grid)
    total_free_cells = sum(1 for y in range(height) for x in range(width) if grid[y][x] == '.')
    visited = [[False for _ in range(width)] for _ in range(height)]

    # Find starting position (first free cell)
    for y in range(height):
        for x in range(width):
            if grid[y][x] == '.':
                start_x, start_y = x, y
                break
        else:
            continue
        break

    # Movement directions and their corresponding deltas
    moves = [
        ('W', 0, -1),  # North
        ('D', 1, 0),   # East
        ('S', 0, 1),   # South
        ('A', -1, 0)   # West
    ]

    path = []

    def dfs(x, y, depth):
        if depth == total_free_cells:
            return True

        for direction_char, dx, dy in moves:
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] == '.' and not visited[ny][nx]:
                    visited[ny][nx] = True
                    path.append(direction_char)
                    if dfs(nx, ny, depth + 1):
                        return True
                    path.pop()
                    visited[ny][nx] = False
        return False

    visited[start_y][start_x] = True
    if dfs(start_x, start_y, 1):
        return path
    else:
        return None


if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=None, test=False, plot_all=False)
