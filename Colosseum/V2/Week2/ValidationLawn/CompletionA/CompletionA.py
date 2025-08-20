import typing
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import deque
import sys
import threading

# Optional imports for plotting
import matplotlib.pyplot as plt
import matplotlib.patches as patches

DIRECTIONS = {
    'W': (0, -1),
    'A': (-1, 0),
    'S': (0, 1),
    'D': (1, 0),
}

@dataclass
class Cell:
    x: int
    y: int

def l4(raw_input: str, plot: bool = False) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))
    outputs = []

    for _ in range(n):
        # Read lawn dimensions
        dimensions = lines.pop(0).split()
        width, height = map(int, dimensions)
        
        # Read lawn grid
        lawn = [list(lines.pop(0)) for _ in range(height)]
        
        path = solve_lawn(lawn, width, height)
        if path is None:
            outputs.append("NO PATH FOUND")
        else:
            outputs.append(path)
            
            if plot:
                plot_lawn_path(lawn, path)

    return "\n".join(outputs)

def solve_lawn(lawn: List[List[str]], width: int, height: int) -> Optional[str]:
    # Find all free cells
    free_cells = {(x, y) for y in range(height) for x in range(width) if lawn[y][x] == '.'}
    
    # Start from any free cell
    for start in free_cells:
        path = []
        visited = set()
        if backtrack(lawn, width, height, start[0], start[1], visited, path, len(free_cells)):
            return path_to_directions(path)
    return None

def backtrack(lawn: List[List[str]], width: int, height: int, x: int, y: int,
              visited: Set[Tuple[int, int]], path: List[Tuple[int, int]],
              total_cells: int) -> bool:
    visited.add((x, y))
    path.append((x, y))
    
    if len(visited) == total_cells:
        return True
    
    # Order of directions can be randomized or optimized
    for dir, (dx, dy) in DIRECTIONS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and lawn[ny][nx] == '.' and (nx, ny) not in visited:
            if backtrack(lawn, width, height, nx, ny, visited, path, total_cells):
                return True
    
    # Backtrack
    visited.remove((x, y))
    path.pop()
    return False

def path_to_directions(path: List[Tuple[int, int]]) -> str:
    directions = ''
    for i in range(1, len(path)):
        x1, y1 = path[i-1]
        x2, y2 = path[i]
        dx = x2 - x1
        dy = y2 - y1
        for dir, (ddx, ddy) in DIRECTIONS.items():
            if dx == ddx and dy == ddy:
                directions += dir
                break
    return directions

def plot_lawn_path(lawn: List[List[str]], path: List[Tuple[int, int]]):
    height = len(lawn)
    width = len(lawn[0]) if height > 0 else 0
    fig, ax = plt.subplots()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()
    
    # Draw lawn grid
    for y in range(height):
        for x in range(width):
            rect = patches.Rectangle((x, y), 1, 1, linewidth=1, edgecolor='black',
                                     facecolor='green' if lawn[y][x] == '.' else 'brown')
            ax.add_patch(rect)
    
    # Draw path
    path_x = [x + 0.5 for x, y in path]
    path_y = [y + 0.5 for x, y in path]
    ax.plot(path_x, path_y, linewidth=2, color='blue')
    
    plt.show()

# Setup threading to increase recursion limit if necessary
def main():
    import sys
    threading.stack_size(1 << 27)
    sys.setrecursionlimit(1 << 25)

    def run():
        raw_input = sys.stdin.read()
        result = l4(raw_input, plot=False)
        print(result)

    threading.Thread(target=run).start()

if __name__ == "__main__":
    main()
