from __future__ import annotations

import sys
import typing
from typing import Any, Callable, Iterable, NamedTuple

import networkx as nx
import matplotlib.pyplot as plt

from .vector import DIRECTIONS  # Assumed to be defined elsewhere

# Type alias for a grid of generic type T
type Grid[T] = list[list[T]]


class Vertex(NamedTuple):
    x: int
    y: int


class Matrix:
    graph: nx.Graph
    grid: Grid

    def __init__(self, graph: nx.Graph, grid: Grid) -> None:
        self.graph = graph
        self.grid = grid

    def __iter__(self) -> Iterable[Vertex]:
        return iter(self.graph.nodes)

    @property
    def num_vertices(
        self,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> int:
        return self.subgraph(filter).number_of_nodes()

    @property
    def num_links(
        self,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> int:
        return self.subgraph(filter).number_of_edges()

    @property
    def coordinate_dict(self) -> dict[Vertex, tuple[float, float]]:
        return {node: (node.x, node.y) for node in self.graph.nodes}

    @property
    def symbol_dict(self) -> dict[Vertex, str]:
        return {node: self.grid[node.y][node.x] for node in self.graph.nodes}

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def columns(self) -> int:
        return len(self.grid[0])

    @property
    def boundary(
        self,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> Matrix:
        return self.submatrix(
            filter=lambda node: filter(node)
            and (node.x in [0, self.columns - 1] or node.y in [0, self.rows - 1])
        )

    def vertices(
        self,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> typing.Sequence[Vertex]:
        return self.subgraph(filter).nodes

    def has_vertex(
        self,
        node: Vertex,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> bool:
        return self.subgraph(filter).has_node(node)

    def subgraph(self, filter: Callable[[Vertex], bool]) -> nx.Graph:
        return self.graph.subgraph([node for node in self.graph.nodes if filter(node)])

    def submatrix(self, filter: Callable[[Vertex], bool]) -> Matrix:
        return Matrix(self.subgraph(filter), self.grid)

    def shortest_route(
        self,
        start: Vertex,
        end: Vertex,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> Iterable[Vertex]:
        return nx.shortest_path(
            self.subgraph(filter),
            source=start,
            target=end,
        )

    def has_route(
        self,
        start: Vertex,
        end: Vertex,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> bool:
        return nx.has_path(
            self.subgraph(filter),
            source=start,
            target=end,
        )

    def neighbors(
        self,
        node: Vertex,
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> Iterable[Vertex]:
        return self.subgraph(filter).neighbors(node)

    def graph_plot(
        self,
        node_color: str = "skyblue",
        filter: Callable[[Vertex], bool] = lambda node: True,
    ) -> None:
        nx.draw(
            self.subgraph(filter),
            pos=self.coordinate_dict,
            labels=self.symbol_dict,
            with_labels=True,
            node_color=node_color,
            node_size=500,
            font_size=10,
            font_weight="bold",
        )

    def plot_shortest_route(
        self,
        start: Vertex,
        end: Vertex,
        filter: Callable[[Vertex], bool] = lambda node: True,
        node_color: str = "orange",
        edge_color: str = "red",
    ) -> None:
        route = nx.shortest_path(
            self.subgraph(filter),
            source=start,
            target=end,
        )
        route_edges = list(zip(route, route[1:]))
        nx.draw_networkx_nodes(
            self.graph,
            self.coordinate_dict,
            nodelist=route,
            node_color=node_color,
        )
        nx.draw_networkx_edges(
            self.graph,
            self.coordinate_dict,
            edgelist=route_edges,
            edge_color=edge_color,
            width=2,
        )

    @staticmethod
    def from_grid(
        input_grid: Grid | list[typing.Sequence],
        directions: list[tuple[int, int]] | None = DIRECTIONS,
        node_attrs: Callable[[Vertex], dict[str, Any]] = lambda node: {},
        edge_attrs: Callable[[Vertex, Vertex], dict[str, Any]] = lambda a, b: {},
    ) -> Matrix:
        graph = nx.Graph()
        grid: list[list] = []
        for y, row in enumerate(input_grid):
            grid.append([])
            for x, cell in enumerate(row):
                v = Vertex(x, y)
                graph.add_node(v, char=cell, **node_attrs(v))
                grid[y].append(cell)
                if directions is not None:
                    for dx, dy in directions:
                        if 0 <= x + dx < len(input_grid[y]) and 0 <= y + dy < len(input_grid):
                            graph.add_edge(
                                v,
                                Vertex(x + dx, y + dy),
                                **edge_attrs(v, Vertex(x + dx, y + dy)),
                            )
        return Matrix(graph=graph, grid=grid)


# -------------------------------
# Level 4 solver: determine valid routes
# -------------------------------
def solve_level4(raw_input: str, plot: bool) -> str:
    """
    For each lawn (given as a grid of characters) with one tree (marked 'X')
    and free cells ('.'), determine a valid route (a string of letters)
    that:
      ▪ covers every free cell exactly once
      ▪ never revisits a cell
      ▪ avoids the tree
      ▪ never leaves the lawn’s boundaries.
    The directions are:
      North – W (move up)
      East  – D (move right)
      South – S (move down)
      West  – A (move left)
    Input:
      The first line is an integer N, the number of lawns.
      Then for each lawn:
         • A line with two integers: lawn_width and lawn_height.
         • lawn_height lines, each with lawn_width characters ('.' or 'X').
    Output:
      For each lawn, output a single line containing the route string.
    If plotting is enabled, the route and lawn will be displayed.
    """
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))
    output: list[str] = []

    # Define the possible moves:
    moves = [
        (0, -1, "W"),  # North: up (decrease y)
        (1, 0, "D"),   # East: right (increase x)
        (0, 1, "S"),   # South: down (increase y)
        (-1, 0, "A"),  # West: left (decrease x)
    ]

    lawn_index = 0
    for _ in range(n):
        lawn_index += 1
        # Read dimensions
        try:
            lawn_width, lawn_height = map(int, lines.pop(0).split())
        except ValueError:
            # Not enough lines?
            break

        # Read lawn grid
        lawn: list[list[str]] = [list(lines.pop(0).strip()) for _ in range(lawn_height)]
        # Count free cells
        total_free = sum(cell == '.' for row in lawn for cell in row)
        # (The tree cell marked 'X' is not free.)
        
        # We choose the top–left corner as start; since the tree is not on the boundary,
        # (0,0) is guaranteed to be free.
        start = (0, 0)
        if lawn[0][0] != '.':
            # Fallback: choose the top–right corner.
            start = (lawn_width - 1, 0)
            if lawn[0][lawn_width - 1] != '.':
                # Should not happen because the tree is not on the boundary.
                raise ValueError("No valid starting cell found on the boundary.")

        solution: str | None = None
        visited: set[tuple[int, int]] = set()

        # Depth-first search (recursive backtracking) for a Hamiltonian path.
        def dfs(x: int, y: int, path: str) -> None:
            nonlocal solution
            if solution is not None:
                return  # already found a valid route
            if len(visited) == total_free:
                solution = path
                return
            for dx, dy, symbol in moves:
                nx_, ny_ = x + dx, y + dy
                # Check boundaries
                if not (0 <= nx_ < lawn_width and 0 <= ny_ < lawn_height):
                    continue
                # Avoid tree and already visited cells
                if lawn[ny_][nx_] != '.':
                    continue
                if (nx_, ny_) in visited:
                    continue
                visited.add((nx_, ny_))
                dfs(nx_, ny_, path + symbol)
                visited.remove((nx_, ny_))
                if solution is not None:
                    return

        visited.add(start)
        dfs(start[0], start[1], "")

        if solution is None:
            # According to the problem description every lawn can be solved.
            output.append("IMPOSSIBLE")
        else:
            output.append(solution)

        if plot:
            # Plot the lawn and route using the Matrix class and networkx.
            # Build a route graph from the solution.
            route_nodes: list[Vertex] = []
            cur = Vertex(start[0], start[1])
            route_nodes.append(cur)
            for ch in solution or "":
                if ch == "W":
                    dx, dy = 0, -1
                elif ch == "D":
                    dx, dy = 1, 0
                elif ch == "S":
                    dx, dy = 0, 1
                elif ch == "A":
                    dx, dy = -1, 0
                else:
                    continue
                cur = Vertex(cur.x + dx, cur.y + dy)
                route_nodes.append(cur)

            route_graph = nx.DiGraph()
            route_graph.add_nodes_from(route_nodes)
            route_graph.add_edges_from(zip(route_nodes, route_nodes[1:]))

            # Create a Matrix for the lawn (we use the full grid; the tree remains).
            matrix = Matrix.from_grid(lawn, directions=None)
            plt.figure()
            plt.gca().invert_yaxis()
            plt.title(f"Lawn {lawn_index}")
            # Plot all free cells (in green) ignoring the tree.
            walkable = matrix.submatrix(filter=lambda node: matrix.symbol_dict[node] != "X")
            walkable.graph_plot(node_color="lightgreen")
            # Plot the route (in blue)
            pos = {Vertex(v.x, v.y): (v.x, v.y) for v in route_graph.nodes}
            nx.draw(route_graph, pos=pos, with_labels=True, node_color="blue", arrows=True)
            plt.show()

    return "\n".join(output)


# -------------------------------
# If running as a script, you might call the solver like this:
# (Note: In the actual game framework the Solver class is used; here we show standalone usage.)
# -------------------------------
if __name__ == "__main__":
    # Read entire input from standard input.
    raw_input = sys.stdin.read()
    # Set plot to True if you wish to see visualizations; otherwise False.
    result = solve_level4(raw_input, plot=False)
    print(result)
