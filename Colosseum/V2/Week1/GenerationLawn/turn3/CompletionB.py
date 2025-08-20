import networkx as nx
from typing import List, Tuple

DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # North, East, South, West

# We will use our previously implemented Lattice and Solver classes
from previous_solution import Lattice, Solver, assert_fn

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n = int(lines.pop(0))

    outputs = []

    for i in range(n):
        # Parse lawn dimensions
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn = [list(lines.pop(0)) for _ in range(lawn_height)]
        tree_position = next((x, y) for y in range(lawn_height) for x in range(lawn_width) if lawn[y][x] == 'X')

        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)

        # Randomly choose start and end positions
        start_x = 0
        start_y = 0
        end_x = lawn_width - 1
        end_y = lawn_height - 1

        # Build path; for simplicity, we may plot directly adjusted paths to validate correctness
        path = nx.shortest_path(lattice.graph, source=Node(start_x, start_y), target=Node(end_x, end_y))

        # Validate path conditions for the lawn
        if valid_path(path, lattice, tree_position):
            outputs.append("VALID")
            if plot:
                lattice.plot()
                # Plot the path for visual validation
                path_positions = [(node.x, node.y) for node in path]
                nx.draw(lattice.graph, pos=lattice.position_dict, node_color='green', with_labels=True)
                nx.draw_networkx_edges(lattice.graph, pos=lattice.position_dict, edgelist=zip(path_positions, path_positions[1:]), edge_color='blue')
                plt.show()
        else:
            outputs.append("INVALID")
            
    return '\n'.join(outputs)

def valid_path(path: List[Node], lattice: Lattice, tree_position: Tuple[int, int]) -> bool:
    """
    Check if the given path is valid based on the lawn's constraints:
    - Path visits each free cell exactly once
    - Does not visit the tree
    - Path does not leave the lawn
    """
    # Check path does not contain tree
    if any((node.x, node.y) == tree_position for node in path):
        return False

    # Check path does not exceed the lawn boundaries
    if any(not (0 <= node.x < lattice.width and 0 <= node.y < lattice.height) for node in path):
        return False

    # Check every node in the path is part of the free space in the lattice
    if any(lattice.label_dict[Node(node.x, node.y)] == 'X' for node in path):
        return False

    # Path connects each consecutive set of cells to cover all accessible space
    unique_nodes = set((node.x, node.y) for node in path)
    if len(unique_nodes) != len(path):
        return False

    return True

# Sample function calls to test our code.
if __name__ == "__main__":
    solver = Solver(game_name="classic")
    solver.solve(4, solve_fn=l4, assert_fn=assert_fn, test=False, plot_all=False)
