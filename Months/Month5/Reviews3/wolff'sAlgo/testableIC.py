import numpy as np
import random
import matplotlib.pyplot as plt

def neighbours(L: int, x: int, y: int) -> list[tuple[int, int]]:
    return [(x, (y-1) % L), (x, (y+1) % L), ((x-1) % L, y), ((x+1) % L, y)]

def wolff_step(grid: np.ndarray, beta: float, q: int) -> int:
    L = len(grid)
    x, y = random.randint(0, L-1), random.randint(0, L-1)
    cluster_spin = grid[x, y]
    cluster = [(x, y)]
    cluster_set = set(cluster)
    
    prob_add = 1 - np.exp(-beta)
    
    stack = [(x, y)]
    
    while stack:
        cx, cy = stack.pop()
        for nx, ny in neighbours(L, cx, cy):
            if (nx, ny) not in cluster_set and grid[nx, ny] == cluster_spin:
                if random.random() < prob_add:
                    cluster.append((nx, ny))
                    cluster_set.add((nx, ny))
                    stack.append((nx, ny))
    
    new_spin = random.choice([s for s in range(q) if s != cluster_spin])
    for cx, cy in cluster:
        grid[cx, cy] = new_spin

    return len(cluster)

def simulate_potts(L: int, q: int, beta: float, steps: int) -> tuple[np.ndarray, list[int]]:
    grid = np.random.randint(0, q, (L, L))
    
    cluster_sizes = []
    
    for step in range(steps):
        cluster_size = wolff_step(grid, beta, q)
        cluster_sizes.append(cluster_size)
        
        if step % (steps // 10) == 0:
            plt.imshow(grid, cmap='tab20')
            plt.title(f"Step {step}")
            plt.show()
    
    return grid, cluster_sizes
