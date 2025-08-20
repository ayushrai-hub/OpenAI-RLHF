import networkx as nx
from typing import List, Tuple, Set, Dict, Optional

def find_hamiltonian_path(graph: nx.Graph, start_node: Tuple[int, int], total_nodes: int) -> Optional[List[Tuple[int, int]]]:
    """
    Finds a Hamiltonian path in the given graph starting from start_node using backtracking.
    Returns the path as a list of nodes or None if no path is found.
    """
    path = [start_node]
    visited = {start_node}

    def backtrack(current_node: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        # If all nodes are visited, we found a path
        if len(visited) == total_nodes:
            return path.copy()

        # Explore neighbors
        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)

                res = backtrack(neighbor)
                if res:
                    return res

                # Backtrack
                visited.remove(neighbor)
                path.pop()
        return None

    return backtrack(start_node)


def convert_path_to_directions(path: List[Tuple[int, int]]) -> str:
    """
    Converts a list of path nodes to direction strings ('W', 'A', 'S', 'D').
    """
    direction_map = {(-1, 0): 'W', (1, 0): 'S', (0, -1): 'A', (0, 1): 'D'}
    directions = []

    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        dx, dy = x2 - x1, y2 - y1
        directions.append(direction_map[(dx, dy)])
    
    return ''.join(directions)


def solve_level4(raw_input: str, plot: bool = False) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))
    outputs = []

    for lawn_index in range(n):
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0).strip()) for _ in range(lawn_height)]

        # Create graph and identify start positions
        walkable_nodes = []
        graph = nx.Graph()
        
        for y in range(lawn_height):
            for x in range(lawn_width):
                if lawn[y][x] == '.':
                    walkable_nodes.append((x, y))
                    # Add edges to adjacent nodes if they're walkable
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx_, ny_ = x + dx, y + dy
                        if 0 <= nx_ < lawn_width and 0 <= ny_ < lawn_height and lawn[ny_][nx_] == '.':
                            graph.add_edge((x, y), (nx_, ny_))

        total_free_cells = len(walkable_nodes)

        # Attempt to find a Hamiltonian Path starting from any walkable position
        found = False
        for start in walkable_nodes:
            path = find_hamiltonian_path(graph, start, total_free_cells)
            if path:
                # Convert the path to directions and append to outputs
                directions = convert_path_to_directions(path)
                outputs.append(directions)
                found = True
                break  # Exit once a path is found

        if not found:
            outputs.append("UNSOLVABLE")

    return '\n'.join(outputs)


# The Solver and assertion function can be reused
# Assuming the existing Solver class implementation and assert_fn from previous levels
if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=solve_level4, assert_fn=assert_fn, test=False, plot_all=False)
