def create_valid_path(lawn: list[list[str]], start: Node) -> list[Node]:
    width = len(lawn[0])
    height = len(lawn)
    directions = {"D": (1, 0), "A": (-1, 0), "S": (0, 1), "W": (0, -1)}
    visited = set()
    path = []
    
    # Use a queue to implement BFS
    queue = [start]
    while queue:
        node = queue.pop(0)
        
        # Ensure node is within boundaries and hasn't been visited
        if (
            0 <= node.x < width
            and 0 <= node.y < height
            and node not in visited
            and lawn[node.y][node.x] != "X"
        ):
            path.append(node)
            visited.add(node)
            
            # Append possible next moves in the order: East, West, South, North
            for direction in ["D", "A", "S", "W"]:
                dx, dy = directions[direction]
                next_node = Node(node.x + dx, node.y + dy)
                if next_node not in visited:
                    queue.append(next_node)
    
    return path

# Convert the path to WASD
def path_to_wasd(path: list[Node]) -> str:
    wasd = ""
    directions = {"D": (1, 0), "A": (-1, 0), "S": (0, 1), "W": (0, -1)}
    for i in range(1, len(path)):
        dx, dy = path[i].x - path[i-1].x, path[i].y - path[i-1].y
        for direction, (dir_x, dir_y) in directions.items():
            if (dx, dy) == (dir_x, dir_y):
                wasd += direction
                break
    return wasd
