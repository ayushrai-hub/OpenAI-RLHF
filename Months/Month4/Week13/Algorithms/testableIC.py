import heapq
import random
import time

class DijkstraComparison:
    def __init__(self):
        self.timing_results: dict = {'matrix': [], 'list': []}
        self.vertex_sizes: list = [50, 100, 200, 400, 800]

    def validate_input(self, graph: list, src: int, is_matrix: bool = True) -> None:
        V = len(graph)
        assert 0 <= src < V, "Source vertex is out of bounds!"
        if is_matrix:
            assert all(len(row) == V for row in graph), "Adjacency matrix must be square!"
        else:
            assert all(isinstance(lst, list) for lst in graph), "Adjacency list must be a list of lists!"

    def matrix_dijkstra(self, graph: list, src: int) -> list:
        V = len(graph)
        dist = [float('inf')] * V
        dist[src] = 0
        sptSet = [False] * V

        for _ in range(V):
            u = self.find_min_distance(dist, sptSet, V)
            sptSet[u] = True
            for v in range(V):
                if graph[u][v] > 0 and not sptSet[v] and dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u] + graph[u][v]

        return dist

    def find_min_distance(self, dist, sptSet, V):
        min_value = float('inf')
        min_idx = -1
        for v in range(V):
            if not sptSet[v] and dist[v] < min_value:
                min_value = dist[v]
                min_idx = v
        return min_idx

    def list_dijkstra(self, adj_list: list, src: int) -> list:
        V = len(adj_list)
        dist = [float('inf')] * V
        dist[src] = 0
        finalized = [False] * V

        min_heap = [(0, src)]
        heapq.heapify(min_heap)

        while min_heap:
            curr_dist, u = heapq.heappop(min_heap)

            if finalized[u]:
                continue
            finalized[u] = True

            for v, weight in adj_list[u]:
                if not finalized[v] and dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    heapq.heappush(min_heap, (dist[v], v))

        return dist

    def generate_graphs(self, V: int) -> tuple:
        matrix = [[0] * V for _ in range(V)]
        adj_list = [[] for _ in range(V)]
        edges = random.randint(V, V * (V - 1) // 2)  # Random number of edges for variety

        for _ in range(edges):
            u = random.randint(0, V - 1)
            v = random.randint(0, V - 1)
            if u != v:
                weight = random.randint(1, 10)
                matrix[u][v] = weight
                matrix[v][u] = weight
                adj_list[u].append((v, weight))
                adj_list[v].append((u, weight))

        return matrix, adj_list

    def run_comparison(self) -> None:
        for V in self.vertex_sizes:
            matrix, adj_list = self.generate_graphs(V)

            start_time = time.perf_counter()
            self.matrix_dijkstra(matrix, 0)
            end_time = time.perf_counter()
            self.timing_results['matrix'].append(end_time - start_time)

            start_time = time.perf_counter()
            self.list_dijkstra(adj_list, 0)
            end_time = time.perf_counter()
            self.timing_results['list'].append(end_time - start_time)

    def plot_results(self) -> None:
        import matplotlib.pyplot as plt

        plt.plot(self.vertex_sizes, self.timing_results['matrix'], label='Adjacency Matrix')
        plt.plot(self.vertex_sizes, self.timing_results['list'], label='Adjacency List')
        plt.xlabel('Number of Vertices')
        plt.ylabel('Time (seconds)')
        plt.title('Dijkstra\'s Algorithm Performance: Matrix vs List')
        plt.legend()
        plt.show()