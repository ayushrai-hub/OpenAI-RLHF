from networkx.algorithms.approximation import traveling_salesman_problem
from networkx.algorithms.approximation import greedy_tsp

def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    graph_i = 0
    while lines:
        graph_i += 1

        # Parse lawn dimensions and lawn data
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        # Build lattice and filter walkable nodes
        lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
        walkable = lattice.subgraph(lambda node: lattice.label_dict[node] != "X")

        # Approximate Hamiltonian path using TSP
        path_nodes = traveling_salesman_problem(walkable, cycle=False, method=greedy_tsp)
        path_string = translate_path_to_directions(path_nodes)

        # Plot if needed
        if plot:
            plt.gca().invert_yaxis()
            plt.title(f"Graph {graph_i}")
            lattice.plot(node_color="green")
            nx.draw(
                walkable, pos=lattice.position_dict,
                labels=lattice.label_dict, with_labels=True, node_color="blue"
            )
            plt.show()

        output.append(path_string)

    return "\n".join(output)


def translate_path_to_directions(path: list[Node]) -> str:
    wasd = ""
    for i in range(1, len(path)):
        dx, dy = path[i].x - path[i - 1].x, path[i].y - path[i - 1].y
        if dx == 1:    wasd += "D"
        elif dx == -1: wasd += "A"
        elif dy == 1:  wasd += "S"
        elif dy == -1: wasd += "W"
    return wasd
