
def find_level4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    
    output: list[str] = []
    
    graph_i = 0
    while lines:
        graph_i += 1
        
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]
        
        matrix = Matrix.from_grid(lawn, directions=DIRECTIONS)
        walkable = matrix.submatrix(filter=lambda node: matrix.symbol_dict[node] != "X")
        
        # Find a valid Hamiltonian path
        # Start from any boundary cell
        boundary_nodes = list(walkable.boundary.vertices())
        if not boundary_nodes:
            output.append("")
            continue
            
        start = boundary_nodes[0]
        path = find_hamiltonian_path(walkable.graph, start)
        
        if path is None:
            output.append("")
            continue
            
        # Convert path to direction string
        route = path_to_directions(path)
        output.append(route)
        
        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            walkable.graph_plot(node_color="green")
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(walkable.graph, walkable.coordinate_dict, 
                                 edgelist=path_edges, edge_color="red", width=2)
            plt.show()
    
    return "\n".join(output)

def find_hamiltonian_path(graph: nx.Graph, start: Vertex) -> list[Vertex] | None:
    def backtrack(path: list[Vertex], visited: set[Vertex]) -> list[Vertex] | None:
        if len(visited) == len(graph):
            return path
            
        current = path[-1]
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                result = backtrack(path, visited)
                if result is not None:
                    return result
                visited.remove(neighbor)
                path.pop()
        return None
    
    visited = {start}
    return backtrack([start], visited)

def path_to_directions(path: list[Vertex]) -> str:
    result = []
    for i in range(len(path) - 1):
        current, next_vertex = path[i], path[i + 1]
        dx = next_vertex.x - current.x
        dy = next_vertex.y - current.y
        
        if dx == 1:
            result.append('D')  # East
        elif dx == -1:
            result.append('A')  # West
        elif dy == 1:
            result.append('S')  # South
        elif dy == -1:
            result.append('W')  # North
            
    return "".join(result)

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=find_level4, assert_fn=assert_fn, test=False, plot_all=False)
