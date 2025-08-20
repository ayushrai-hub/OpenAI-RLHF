from typing import NamedTuple, List, Dict, Tuple
import networkx as nx
from dataclasses import dataclass

class Point(NamedTuple):
    x: int
    y: int

@dataclass
class Lattice:
    graph: nx.Graph
    grid: List[List[str]]
    
    def __iter__(self):
        return iter(self.graph.nodes)
    
    def has_point(self, node: Point) -> bool:
        return self.graph.has_node(node)
    
    @staticmethod
    def from_grid(grid: List[List[str]], directions: List[Tuple[int, int]], 
                 node_attributes=lambda p: {}) -> 'Lattice':
        graph = nx.Graph()
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                graph.add_node(Point(x, y), **node_attributes(Point(x, y)))
                for dx, dy in directions:
                    if (0 <= x + dx < len(grid[y]) and 
                        0 <= y + dy < len(grid)):
                        graph.add_edge(
                            Point(x, y),
                            Point(x + dx, y + dy)
                        )
        return Lattice(graph=graph, grid=grid)

def solve_lawn_mower(raw_input: str) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))  # Number of test cases
    
    output = []
    cursor = 0
    
    # Define direction mapping
    directions = {
        'W': (0, 1),   # North
        'D': (1, 0),   # East
        'S': (0, -1),  # South
        'A': (-1, 0)   # West
    }
    
    while cursor < len(lines):
        # Parse lawn dimensions and path
        h, w = map(int, lines[cursor].split())
        cursor += 1
        
        # Build grid
        grid = []
        tree_pos = None
        for y in range(h):
            row = list(lines[cursor])
            if 'X' in row:
                tree_pos = Point(row.index('X'), h - 1 - y)
            grid.insert(0, row)  # Reverse y-axis so (0,0) is bottom-left
            cursor += 1
        
        path = lines[cursor]
        cursor += 1
        
        # Create lattice (only connect adjacent free cells)
        lattice = Lattice.from_grid(
            grid,
            directions=[(1,0), (-1,0), (0,1), (0,-1)],  # 4 cardinal directions
            node_attributes=lambda p: {'free': grid[p.y][p.x] == '.'}
        )
        
        # Find starting position (first free cell)
        start = next(p for p in lattice if lattice.graph.nodes[p]['free'])
        
        # Follow the path
        current = start
        visited = {current}
        
        valid = True
        for move in path:
            dx, dy = directions[move]
            next_pos = Point(current.x + dx, current.y + dy)
            
            # Check if move is valid
            if (not lattice.has_point(next_pos) or  # Out of bounds
                next_pos == tree_pos or             # Hits tree
                not lattice.graph.nodes[next_pos]['free'] or  # Not free cell
                next_pos in visited):               # Already visited
                valid = False
                break
                
            current = next_pos
            visited.add(current)
        
        # Check if all free cells were visited
        free_cells = sum(1 for p in lattice if lattice.graph.nodes[p]['free'])
        if len(visited) != free_cells:
            valid = False
            
        output.append("VALID" if valid else "INVALID")
    
    return "\n".join(output)

# Test cases
def test_lawn_mower():
    # Test case 1: Simple valid path
    test_input1 = """1
3 3
...
.X.
...
WDSDASA"""
    assert solve_lawn_mower(test_input1) == "VALID"

    # Test case 2: Invalid path (doesn't visit all cells)
    test_input2 = """1
3 3
...
.X.
...
WDS"""
    assert solve_lawn_mower(test_input2) == "INVALID"

    # Test case 3: Invalid path (hits tree)
    test_input3 = """1
3 3
...
.X.
...
WDWD"""
    assert solve_lawn_mower(test_input3) == "INVALID"

    # Test case 4: Invalid path (out of bounds)
    test_input4 = """1
3 3
...
.X.
...
WDWDWDWD"""
    assert solve_lawn_mower(test_input4) == "INVALID"

    # Test case 5: Multiple test cases
    test_input5 = """2
3 3
...
.X.
...
WDSDASA
2 2
..
X.
DA"""
    assert solve_lawn_mower(test_input5) == "VALID\nVALID"

    print("All tests passed!")

if __name__ == "__main__":
    test_lawn_mower()