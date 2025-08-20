import networkx as nx
from itertools import product
import random

def generate_level4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    for _ in range(n):
        lawn_width, lawn_height = tuple(map(int, lines.pop(0).split()))
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        matrix = Matrix.from_grid(lawn, directions=DIRECTIONS)
        walkable = matrix.submatrix(filter=lambda node: matrix.symbol_dict[node] != "X")

        # Find a valid path
        path = find_valid_path(walkable, lawn_width, lawn_height)

        if path:
            route = path_to_route(path)
            output.append(route)
        else:
            output.append("NO VALID PATH")

        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Lawn {_+1}")
            walkable.graph_plot(node_color="green")
            if path:
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(walkable.graph, walkable.coordinate_dict, edgelist=path_edges, edge_color="red", width=2)
            plt.show()

    return "\n".join(output)

def find_valid_path(walkable: Matrix, width: int, height: int) -> list[Vertex] | None:
    all_nodes = list(walkable.vertices())
    
    for start in all_nodes:
        path = hamiltonian_path(walkable, start, width, height)
        if path:
            return path
    
    return None

def hamiltonian_path(walkable: Matrix, start: Vertex, width: int, height: int) -> list[Vertex] | None:
    def dfs(node: Vertex, path: list[Vertex]) -> list[Vertex] | None:
        if len(path) == walkable.num_vertices:
            return path
        
        for neighbor in walkable.neighbors(node):
            if neighbor not in path:
                result = dfs(neighbor, path + [neighbor])
                if result:
                    return result
        
        return None

    return dfs(start, [start])

def path_to_route(path: list[Vertex]) -> str:
    route = []
    for i in range(len(path) - 1):
        current, next = path[i], path[i+1]
        if next.x > current.x:
            route.append('D')
        elif next.x < current.x:
            route.append('A')
        elif next.y > current.y:
            route.append('S')
        elif next.y < current.y:
            route.append('W')
    return ''.join(route)

if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=generate_level4, assert_fn=assert_fn, test=False, plot_all=False)
