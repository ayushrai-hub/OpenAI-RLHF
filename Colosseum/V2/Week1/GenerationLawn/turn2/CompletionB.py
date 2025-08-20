from __future__ import annotations
import typing
from typing import Any, Callable, Iterable, NamedTuple
import networkx as nx
from vector import ALL_DIRECTIONS

type Grid[T] = list[list[T]]

class Node(NamedTuple):
    x: int
    y: int

class Lattice:
    graph: nx.Graph
    grid: Grid

    def __init__(self, graph: nx.Graph, grid: Grid) -> None:
        self.graph = graph
        self.grid = grid

    def __iter__(self) -> Iterable[Node]:
        return iter(self.graph.nodes)

    @property
    def num_nodes(self,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> int:
        return self.subgraph(only).number_of_nodes()

    @property
    def num_edges(self,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> int:
        return self.subgraph(only).number_of_edges()

    @property
    def position_dict(self) -> dict[Node, tuple[float, float]]:
        return {node: (node.x, node.y) for node in self.graph.nodes}

    @property
    def label_dict(self) -> dict[Node, str]:
        return {node: self.grid[node.y][node.x] for node in self.graph.nodes}

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def width(self) -> int:
        return len(self.grid[0])

    @property
    def border(
        self,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> Lattice:
        return self.sublattice(
            only=lambda node: only(node) and (node.x in [0, self.width - 1] or node.y in [0, self.height - 1])
        )

    def nodes(
        self,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> typing.Sequence[Node]:
        return self.subgraph(only).nodes

    def has_node(
        self,
        node: Node,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> bool:
        return self.subgraph(only).has_node(node)

    def subgraph(self, only: Callable[[Node], bool]) -> nx.Graph:
        return self.graph.subgraph([node for node in self.graph.nodes if only(node)])

    def sublattice(self, only: Callable[[Node], bool]) -> Lattice:
        return Lattice(self.subgraph(only), self.grid)

    def shortest_path(
        self,
        source: Node,
        target: Node,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> Iterable[Node]:
        return nx.shortest_path(
            self.subgraph(only),
            source=source,
            target=target,
        )

    def has_path(
        self,
        source: Node,
        target: Node,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> bool:
        return nx.has_path(
            self.subgraph(only),
            source=source,
            target=target,
        )

    def neighbors(
        self,
        node: Node,
        only: Callable[[Node], bool] = lambda node: True,
    ) -> Iterable[Node]:
        return self.subgraph(only).neighbors(node)

    def plot(
        self,
        node_color: str = "skyblue",
        only: Callable[[Node], bool] = lambda node: True,
    ) -> None:
        nx.draw(
            self.subgraph(only),
            pos=self.position_dict,
            labels=self.label_dict,
            with_labels=True,
            node_color=node_color,
            node_size=500,
            font_size=10,
            font_weight="bold",
        )

    def plot_shortest_path(
        self,
        source: Node,
        target: Node,
        only: Callable[[Node], bool] = lambda node: True,
        node_color: str = "orange",
        edge_color: str = "red",
    ) -> None:
        path = nx.shortest_path(
            self.subgraph(only),
            source=source,
            target=target,
        )
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(
            self.graph,
            self.position_dict,
            nodelist=path,
            node_color=node_color,
        )
        nx.draw_networkx_edges(
            self.graph,
            self.position_dict,
            edgelist=path_edges,
            edge_color=edge_color,
            width=2,
        )

    @staticmethod
    def from_grid(
        input_sequence: Grid | list[typing.Sequence],
        directions: list[tuple[int, int]] | None = ALL_DIRECTIONS,
        node_attributes: Callable[[Node], dict[str, Any]] = lambda node: {},
        edge_attributes: Callable[[Node, Node], dict[str, Any]] = lambda a, b: {},
    ) -> Lattice:
        graph = nx.Graph()
        grid: list[list] = []
        for y, row in enumerate(input_sequence):
            grid.append([])
            for x, char in enumerate(row):
                graph.add_node(Node(x, y), char=char, **node_attributes(Node(x, y)))
                grid[y].append(char)
                if directions is not None:
                    for dx, dy in directions:
                        if 0 <= x + dx < len(input_sequence[y]) and 0 <= y + dy < len(input_sequence):
                            graph.add_edge(
                                Node(x, y),
                                Node(x + dx, y + dy),
                                **edge_attributes(Node(x, y), Node(x + dx, y + dy)),
                            )
        return Lattice(graph=graph, grid=grid)

def from_input(raw_input: str) -> list[tuple[tuple[int, int], list[list[str]], str]]:
    lines = raw_input.strip().splitlines()
    n = int(lines[0])
    data = []
    line_index = 1
    for _ in range(n):
        w, h = map(int, lines[line_index].split())
        line_index += 1
        lawn = [list(lines[line_index + i]) for i in range(h)]
        line_index += h
        path = lines[line_index]
        line_index += 1
        data.append(((w, h), lawn, path))
    return data

def to_output(results: list[str]) -> str:
    return "\n".join(results)

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def build_path_graph(path: str) -> nx.DiGraph:
    move_map = {'W': (0, -1), 'D': (1, 0), 'S': (0, 1), 'A': (-1, 0)}
    start = (0, 0)
    graph = nx.DiGraph()
    current_pos = start
    visited = set([start])

    for move in path:
        dx, dy = move_map[move]
        next_pos = (current_pos[0] + dx, current_pos[1] + dy)
        
        if next_pos in visited:
            break

        graph.add_edge(current_pos, next_pos)
        visited.add(next_pos)
        current_pos = next_pos

    return graph

def has_valid_path(grid: list[list[str]], path: nx.DiGraph) -> bool:
    width = len(grid[0])
    height = len(grid)

    for node in path.nodes:
        x, y = node
        if not (0 <= x < width and 0 <= y < height):  # Check for out-of-bounds nodes
            return False
        if grid[y][x] == 'X':  # Check for tree cell
            return False
    return True

def l4(data: tuple[tuple[int, int], list[list[str]], str]) -> str:
    (w, h), lawn, path = data

    lattice = Lattice.from_grid(lawn, directions=DIRECTIONS)
    path_graph = build_path_graph(path)
    
