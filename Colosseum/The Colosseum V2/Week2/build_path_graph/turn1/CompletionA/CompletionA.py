import networkx as nx
from typing import List

def build_path_graph(path: str) -> nx.DiGraph:
    # Translate path into a directed graph where nodes represent coordinates
    path_graph = nx.DiGraph()
    if not path:
        return path_graph
    pos = (0, 0)
    path_graph.add_node(pos)
    for direction in path:
        dx, dy = {'W': (0, -1), 'S': (1, 0), 'E': (0, 1), 'A': (-1, 0)}[direction]
        pos = (pos[0] + dx, pos[1] + dy)
        path_graph.add_node(pos)
        path_graph.add_edge(path_graph.nodes[-2], pos)
    return path_graph

def l4(raw_input: str) -> List[str]:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))
    
    results = []

    for _ in range(n):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0)) for _ in range(lawn_height)]
        path = find_valid_path(lawn, lawn_width, lawn_height)

        results.append(path)

    return results

def find_valid_path(lawn: List[List[str]], lawn_width: int, lawn_height: int) -> str:
    '''
    Find a valid path for the lawn, starting at a given position and ending at another,
    ensuring it visits every free cell exactly once and avoids the tree.
    '''
    for start in [(0, 0), (0, lawn_height - 1), (lawn_width - 1, 0), (lawn_width - 1, lawn_height - 1)]:
        if lawn[start[1]][start[0]] == '.':
            break
    else:
        raise ValueError("No valid starting position in the lawn.")

    for end in [(0, 0), (0, lawn_height - 1), (lawn_width - 1, 0), (lawn_width - 1, lawn_height - 1)]:
        if lawn[end[1]][end[0]] == '.' and end != start:
            break
    else:
        raise ValueError("No valid ending position in the lawn.")

    lattice = Lattice.from_grid(lawn, directions=ALL_DIRECTIONS)

    def create_valid_path(lattice: Lattice, start: (int, int), end: (int, int)) -> str:
        # Find a path from start to end that covers the whole lattice
        # Set initial path as a straight line or choose an algorithmic approach to find a path
        path = []

        # Example simple path logic (adjust as needed for better path finding):
        current = start
        path.append(current)
        while current != end:
            next_pos = next_step_to_target(current, end, lattice)
            if next_pos:
                path.append(next_pos)
                current = next_pos
            else:
                raise ValueError("No path found")

        return ''.join(step for step in path)

    path = create_valid_path(lattice, start, end)
    return path

def next_step_to_target(current_pos, target_pos, lattice):
    # Placeholder for logic to decide the next step towards the target
    # Could be DFS, BFS, or other algorithmic approaches
    pass
