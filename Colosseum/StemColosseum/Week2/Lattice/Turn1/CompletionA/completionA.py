from __future__ import annotations

import typing
from typing import Any, Callable, Iterable, NamedTuple, Optional
from collections import deque

import networkx as nx

import sys
import threading

# Direction mappings
direction_map: dict[str, tuple[int, int]] = {'W': (0, -1), 'D': (1, 0), 'S': (0, 1), 'A': (-1, 0)}
delta_to_direction: dict[tuple[int, int], str] = {(0, -1): 'W', (1, 0): 'D', (0, 1): 'S', (-1, 0): 'A'}

# For the Lattice class, define the Grid type
Grid = list[list[str]]

# Define Node as a simple coordinate pair
class Node(NamedTuple):
    x: int
    y: int

# Define the Lattice class to manage the graph
class Lattice:
    def __init__(self, graph: nx.Graph, grid: Grid) -> None:
        self.graph = graph
        self.grid = grid

    @property
    def num_nodes(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def num_edges(self) -> int:
        return self.graph.number_of_edges()

    @property
    def position_dict(self) -> dict[Node, tuple[float, float]]:
        return {node: (node.x, node.y) for node in self.graph.nodes}

    @property
    def label_dict(self) -> dict[Node, str]:
        return {node: self.grid[node.y][node.x] for node in self.graph.nodes}

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def width(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def nodes(self) -> typing.Sequence[Node]:
        return list(self.graph.nodes)

    def has_node(self, node: Node) -> bool:
        return self.graph.has_node(node)

    def neighbors(self, node: Node) -> Iterable[Node]:
        return self.graph.neighbors(node)

    @staticmethod
    def from_grid(
        input_sequence: Grid,
        directions: list[tuple[int, int]] | None = list(direction_map.values()),
    ) -> Lattice:
        graph = nx.Graph()
        grid = input_sequence
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        for y in range(height):
            for x in range(width):
                if grid[y][x] != 'X':
                    node = Node(x, y)
                    graph.add_node(node)
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if grid[ny][nx] != 'X':
                                neighbor = Node(nx, ny)
                                graph.add_edge(node, neighbor)
        return Lattice(graph=graph, grid=grid)

def l4(raw_input: str, plot: bool=False) -> str:
    lines = deque(raw_input.strip().splitlines())
    n: int = int(lines.popleft())

    output: list[str] = []

    for _ in range(n):
        lawn_width_height = lines.popleft()
        while lawn_width_height.strip() == '':
            lawn_width_height = lines.popleft()
        lawn_width, lawn_height = map(int, lawn_width_height.strip().split())
        lawn = []
        while len(lawn) < lawn_height:
            line = lines.popleft()
            if line.strip() != '':
                lawn.append(list(line.strip()))
        # Build the Lattice
        lattice = Lattice.from_grid(lawn)

        # List of free cells
        free_cells = set(lattice.nodes())

        # For simplicity, pick the first free cell as starting point
        start_node = next(iter(free_cells))

        # Function to find Hamiltonian path
        def find_path(current_node: Node, visited: set[Node], path: list[Node]) -> Optional[list[Node]]:
            if len(visited) == len(free_cells):
                return path
            for neighbor in lattice.neighbors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    result = find_path(neighbor, visited, path)
                    if result is not None:
                        return result
                    # backtrack
                    visited.remove(neighbor)
                    path.pop()
            return None

        # Initialize visited set and path list
        visited = {start_node}
        path = [start_node]
        result_path = find_path(start_node, visited, path)
        if result_path is None:
            output.append("NO PATH FOUND")
        else:
            # Build the direction string
            directions = ''
            for i in range(1, len(result_path)):
                x1, y1 = result_path[i-1]
                x2, y2 = result_path[i]
                dx = x2 - x1
                dy = y2 - y1
                dir_char = delta_to_direction.get((dx, dy))
                if dir_char:
                    directions += dir_char
                else:
                    # This should not happen
                    directions += '?'
            output.append(directions)

    return "\n".join(output)

def main():
    import sys
    raw_input = sys.stdin.read()
    result = l4(raw_input)
    print(result)

if __name__ == "__main__":
    threading.Thread(target=main).start()
