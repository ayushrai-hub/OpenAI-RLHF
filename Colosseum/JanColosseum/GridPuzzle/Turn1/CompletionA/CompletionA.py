import networkx as nx
from typing import List, Tuple, Optional, Set

class Node(Tuple[int, int]):
    pass

class Lattice:
    # Placeholder for the actual Lattice class implementation
    pass

def find_valid_path(lawn: List[List[str]], start: Node, tree: Node) -> Optional[str]:
    directions = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'D': (0, 1)}
    path = []
    visited: Set[Node] = set()

    def backtrack(x, y):
        if len(visited) == len(lawn) * len(lawn[0]) - 1:
            return True
        for dir_key, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(lawn[0]) and 0 <= ny < len(lawn) and (ny, nx) != tree and (ny, nx) not in visited:
                visited.add((ny, nx))
                path.append(dir_key)
                if backtrack(nx, ny):
                    return True
                path.pop()
                visited.remove((ny, nx))
        return False

    visited.add(start)
    if backtrack(*start):
        return ''.join(path)
    return None

def solve_lawn_mowing_problem(input_sequence: List[str]) -> str:
    lines = iter(input_sequence)
    n = int(next(lines))
    results = []

    for _ in range(n):
        lawn_width, lawn_height = map(int, next(lines).split())
        lawn = [list(next(lines)) for _ in range(lawn_height)]
        tree_pos = next((Node(x, y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == 'X'))

        # Determine a start point that is not the tree
        start_pos = next(Node(x, y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == '.' and (x, y) != tree_pos)

        path = find_valid_path(lawn, start_pos, tree_pos)
        results.append(path if path else 'NO VALID PATH FOUND')

    return "\n".join(results)

# Example usage
input_data = [
    "1",  # Number of lawns
    "7 6",  # Dimensions of the lawn
    ".......",
    ".......",
    ".......",
    ".......",
    ".X.....",
    "......."
]
print(solve_lawn_mowing_problem(input_data))

