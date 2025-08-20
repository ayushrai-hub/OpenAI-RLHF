def l3_validation(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    lawns = int(lines.pop(0))

    answers = []
    for _ in range(lawns):
        w, h = map(int, lines.pop(0).split())
        grid = [lines.pop(0) for _ in range(h)]

        # Create lattice
        lattice = Lattice.from_grid(grid, directions=DIRECTIONS)
        
        # Get walkable nodes and initial state
        walkable_nodes = {n for n in lattice if lattice.grid[n.y][n.x] != 'X'}
        visited_nodes = set()

        # Use a start node
        start_node = next(iter(walkable_nodes))
        visited_nodes.add(start_node)
        current_node = start_node

        # Continue visiting nearest unvisited node
        valid = True
        while visited_nodes != walkable_nodes:
            unvisited_nodes = walkable_nodes - visited_nodes
            # Find the nearest next node
            try:
                next_node, shortest = min(
                    ((node, path)
                     for node in unvisited_nodes
                     if nx.has_path(lattice.graph, current_node, node)
                     and (path := nx.shortest_path(lattice.graph, current_node, node))),
                    key=lambda x: len(x[1])
                )
                
                # Make sure path doesn't step on visited nodes
                if any(n in visited_nodes for n in shortest[1:]):
                    valid = False
                    break
                
                # Visit nodes
                visited_nodes.update(shortest[1:])
                current_node = next_node
                
            except ValueError:
                # No path found to an unvisited node
                valid = False
                break

        answers.append("VALID" if valid else "INVALID")

    return "\n".join(answers)
