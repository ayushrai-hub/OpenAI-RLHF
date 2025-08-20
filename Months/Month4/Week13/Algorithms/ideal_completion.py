#ideal_completion.py

import heapq
import random
import time
import matplotlib.pyplot as plt

def theoretical_analysis(self):
    """
    Document theoretical time complexity analysis:
    Matrix Implementation:
    - Find-min operation: O(V) per iteration
    - Distance updates: O(V) per iteration
    - Total iterations: O(V)
    - Overall: O(V^2)
    
    List Implementation:
    - Extract-min: O(log V) per operation
    - Distance updates: O(log V) per edge
    - Total: O((V + E)log V)
    """
    pass

class DijkstraComparison:
    def __init__(self):
        self.timing_results = {'matrix': [], 'list': []}
        self.vertex_sizes = [50, 100, 200, 400, 800]
    
    def validate_input(self, graph, src, is_matrix=True):
        """Validate input parameters for both implementations"""
        if not graph:
            raise ValueError("Empty graph is not allowed")
            
        V = len(graph)
        if src < 0 or src >= V:
            raise ValueError(f"Source vertex {src} is out of range [0, {V-1}]")
            
        if is_matrix:
            # Check for negative edges in matrix
            if any(graph[i][j] < 0 for i in range(V) for j in range(V)):
                raise ValueError("Negative edge weights are not allowed")
        else:
            # Check for negative edges in adjacency list
            if any(weight < 0 for adj in graph for _, weight in adj):
                raise ValueError("Negative edge weights are not allowed")
    
    def matrix_dijkstra(self, graph, src):
        """Implementation with adjacency matrix and array-based queue"""
        # Validate input
        self.validate_input(graph, src, is_matrix=True)
        
        V = len(graph)
        dist = [float('inf')] * V
        dist[src] = 0
        sptSet = [False] * V
        
        for _ in range(V):
            min_dist = float('inf')
            min_idx = -1
            # Find minimum distance vertex from unprocessed set
            for v in range(V):
                if not sptSet[v] and dist[v] < min_dist:
                    min_dist = dist[v]
                    min_idx = v
            
            if min_idx == -1:
                break
                
            sptSet[min_idx] = True
            # Update distances of adjacent vertices
            for v in range(V):
                if (graph[min_idx][v] > 0 and not sptSet[v] and
                    dist[min_idx] + graph[min_idx][v] < dist[v]):
                    dist[v] = dist[min_idx] + graph[min_idx][v]
        return dist

    def list_dijkstra(self, adj_list, src):
        """Implementation with adjacency list and min-heap"""
        # Validate input
        self.validate_input(adj_list, src, is_matrix=False)
        
        V = len(adj_list)
        dist = [float('inf')] * V
        dist[src] = 0
        pq = [(0, src)]
        finalized = set()
        
        while pq:
            d, u = heapq.heappop(pq)
            if u in finalized:
                continue
            finalized.add(u)
            
            for v, weight in adj_list[u]:
                if v not in finalized and d + weight < dist[v]:
                    dist[v] = d + weight
                    heapq.heappush(pq, (dist[v], v))
        return dist

    def generate_graphs(self, V):
        """Generate equivalent matrix and list representations"""
        if V <= 0:
            raise ValueError("Number of vertices must be positive")
            
        density = 0.3
        matrix = [[0] * V for _ in range(V)]
        adj_list = [[] for _ in range(V)]
        
        for i in range(V):
            for j in range(i+1, V):
                if random.random() < density:
                    weight = random.randint(1, 10)
                    matrix[i][j] = matrix[j][i] = weight
                    adj_list[i].append((j, weight))
                    adj_list[j].append((i, weight))
        return matrix, adj_list

    def run_comparison(self):
        for V in self.vertex_sizes:
            matrix, adj_list = self.generate_graphs(V)
            
            # Time matrix implementation
            start = time.perf_counter()
            self.matrix_dijkstra(matrix, 0)
            matrix_time = time.perf_counter() - start
            
            # Time list implementation
            start = time.perf_counter()
            self.list_dijkstra(adj_list, 0)
            list_time = time.perf_counter() - start
            
            self.timing_results['matrix'].append(matrix_time)
            self.timing_results['list'].append(list_time)

    def plot_results(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.vertex_sizes, self.timing_results['matrix'], 
                'ro-', label='Matrix Implementation (O(V²))')
        plt.plot(self.vertex_sizes, self.timing_results['list'], 
                'bo-', label='List Implementation (O((V+E)logV))')
        plt.xlabel('Number of Vertices (V)')
        plt.ylabel('Time (seconds)')
        plt.title('Dijkstra\'s Algorithm: Implementation Comparison')
        plt.legend()
        plt.grid(True)
        plt.show()

# Run comparison
comparison = DijkstraComparison()
comparison.run_comparison()
comparison.plot_results()