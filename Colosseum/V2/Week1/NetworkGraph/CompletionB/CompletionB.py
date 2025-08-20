from typing import Iterable
import networkx as nx
from dataclasses import dataclass

DIRECTIONS = {
    'W': (0, -1),  # North
    'D': (1, 0),   # East
    'S': (0, 1),   # South
    'A': (-1, 0),  # West
}

def l3(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    while lines:
        # Parse dimensions and lawn
        width, height = map(int, lines.pop(0).split())
        lawn = [list(row) for row in lines[:height]]
        lines = lines[height:]
        
        # Parse path
        path = lines.pop(0)
        
        # Create lattice and check if path is valid
        lattice = Lattice.from_grid(lawn)
        result = is_valid_path(lattice, path)
        output.append("valid" if result else "invalid")

    return "\n".join(output)

def is_valid_path(lattice: Lattice, path: str) -> bool:
    # Find start position (any free cell)
    start = next(p for p in lattice.points() if lattice.label_dict[p] == '.')
    
    # Track visited positions and current position
    visited = {start}
    current = start
    
    try:
        # Follow the path
        for direction in path:
            dx, dy = DIRECTIONS[direction]
            next_pos = Point(current.x + dx, current.y + dy)
            
            # Check if move is valid:
            # 1. Position exists in graph
            # 2. Not hitting a tree
            # 3. Not visiting twice
            if (not lattice.has_point(next_pos) or 
                lattice.label_dict[next_pos] == 'X' or 
                next_pos in visited):
                return False
            
            visited.add(next_pos)
            current = next_pos
            
        # After path is complete, check if all free cells were visited
        free_cells = {p for p in lattice.points() 
                     if lattice.label_dict[p] == '.'}
        return free_cells == visited
        
    except KeyError:  # Invalid direction in path
        return False

