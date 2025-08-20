def l3(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))  # Number of test cases
    
    output = []
    cursor = 0
    
    # Define direction mapping
    directions = {
        'W': (0, 1),  # North
        'D': (1, 0),  # East
        'S': (0, -1), # South
        'A': (-1, 0)  # West
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
        path_nodes = [current]
        
        for move in path:
            dx, dy = directions[move]
            next_pos = Point(current.x + dx, current.y + dy)
            
            # Check if move is valid
            if (not lattice.has_point(next_pos) or  # Out of bounds
                next_pos == tree_pos or            # Hits tree
                not lattice.graph.nodes[next_pos]['free']):  # Not free cell
                break
                
            current = next_pos
            path_nodes.append(current)
            if current in visited:  # Visited twice
                break
            visited.add(current)
        
        # Check if path is valid:
        # 1. Must visit all free cells
        # 2. Must not hit tree
        # 3. Must not revisit cells
        free_cells = lattice.num_nodes(only=lambda p: lattice.graph.nodes[p]['free'])
        is_valid = (len(visited) == free_cells and  # All free cells visited
                   tree_pos not in visited)         # Didn't hit tree
        
        output.append("VALID" if is_valid else "INVALID")
        
        # Optional plotting
        if plot:
            import matplotlib.pyplot as plt
            lattice.plot(node_color="lightgray")
            lattice.plot_shortest_path(
                start, 
                path_nodes[-1],
                only=lambda p: p in path_nodes,
                node_color="green",
                edge_color="blue"
            )
            plt.title(f"Case {len(output)}: {'VALID' if is_valid else 'INVALID'}")
            plt.show()
    
    return "\n".join(output)

# Example usage with Solver class:
if __name__ == "__main__":
    solver = Solver("lawn_mower")
    
    def assert_fn(expected: str, actual: str) -> None:
        assert expected.strip() == actual.strip(), f"Expected:\n{expected}\nGot:\n{actual}"
    
    solver.solve(
        level=3,
        solve_fn=l3,
        assert_fn=assert_fn,
        test=True,
        plot_all=False
    )
