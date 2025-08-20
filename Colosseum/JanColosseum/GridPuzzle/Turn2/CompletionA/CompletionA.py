def valid_path(lawn: list[list[str]], lawn_width: int, lawn_height: int) -> str:
    # Directions corresponding to (dx, dy) movement and their respective characters
    direction_dict = {
        (0, -1): 'W',  # North
        (1, 0): 'D',   # East
        (0, 1): 'S',   # South
        (-1, 0): 'A'   # West
    }
    
    # Movements: correspond to (dx, dy)
    moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    # Find the starting point (any free cell)
    start_node = None
    for y in range(lawn_height):
        for x in range(lawn_width):
            if lawn[y][x] == '.':
                start_node = Node(x, y)
                break
        if start_node:
            break
    
    # Stack of potential paths to explore, starting with the initial node
    stack = [(start_node, set([start_node]), [])]  # (current_node, visited_nodes, path_so_far)
    
    while stack:
        current_node, visited, path = stack.pop()
        
        # If all free cells are visited, we found a valid path
        if len(visited) == sum(row.count('.') for row in lawn):
            return ''.join(path)
        
        x, y = current_node
        for (dx, dy), d_char in zip(moves, direction_dict.values()):
            nx, ny = x + dx, y + dy
            neighbor = Node(nx, ny)
            
            if 0 <= nx < lawn_width and 0 <= ny < lawn_height and lawn[ny][nx] == '.' and neighbor not in visited:
                stack.append((neighbor, visited | {neighbor}, path + [d_char]))
    
    return ""

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output = []

    for _ in range(n):
        # Dimensions of the lawn
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0)) for _ in range(lawn_height)]  # Build the lawn grid
        
        # Generate a valid path for this lawn
        path = valid_path(lawn, lawn_width, lawn_height)
        output.append(path)
    
    return "\n".join(output)
