import random
import matplotlib.pyplot as plt
import networkx as nx

def find_valid_path(lawn, start=None, end=None, plot=True):
    if not start:
        start = (0, 0)
    if not end:
        end = (len(lawn[0]) - 1, len(lawn) - 1)

    directions = ['N', 'E', 'S', 'W']
    grid_height = len(lawn)
    grid_width = len(lawn[0])
    
    def is_valid_step(x, y):
        if 0 <= x < grid_width and 0 <= y < grid_height and lawn[y][x] == '.':
            return True
        return False

    def next_moves(x, y):
        moves = []
        for dx, dy, direction in [(-1, 0, 'W'), (1, 0, 'E'), (0, -1, 'N'), (0, 1, 'S')]:
            if is_valid_step(x + dx, y + dy):
                moves.append((x + dx, y + dy, direction))
        return moves

    visited = set()
    path = []
    stack = [(start[0], start[1], [])]
    while stack:
        x, y, current_path = stack.pop()
        if (x, y) == end:
            path = current_path
            break
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for nx, ny, direction in next_moves(x, y):
            if (nx, ny) not in visited:
                stack.append((nx, ny, current_path + [direction]))

    if path:
        return "".join(path)
    return None

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    N = int(lines[0])
    result = []

    lines = lines[1:]
    for _ in range(N):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0)) for _ in range(lawn_height)]
        
        # Generate a valid path if possible
        path = find_valid_path(lawn, plot=plot)
        if plot:
            plt.imshow([list(lawn[i]) for i in range(lawn_height)], cmap='Greens')
            plt.title("Lawn with Valid Path")
            plt.scatter([0, lawn_width-1], [0, lawn_height-1], c='red')
            plt.scatter([0, lawn_width-1], [lawn_height-1, 0], c='blue')
            plt.gca().invert_yaxis()  # Invert y-axis so origin is at top-left
            plt.show()
        
        if path:
            result.append(path)
        else:
            result.append("INVALID")

    return "\n".join(result)

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=None, test=False, plot_all=False)
