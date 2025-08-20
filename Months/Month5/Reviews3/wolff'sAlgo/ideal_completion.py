#ideal_completion.py
import numpy as np
import random
import matplotlib.pyplot as plt

# Function to get nearest neighbours with periodic boundaries
def neighbours(L, x, y):
    return [(x, (y-1) % L), (x, (y+1) % L), ((x-1) % L, y), ((x+1) % L, y)]

# Function to implement the Wolff cluster algorithm
def wolff_step(grid, beta, q):
    """Performs a single Wolff cluster update."""
    L = len(grid)
    x, y = random.randint(0, L-1), random.randint(0, L-1)
    cluster_spin = grid[x, y]
    cluster = [(x, y)]
    cluster_set = set(cluster)
    
    # Probability for adding a spin to the cluster
    prob_add = 1 - np.exp(-beta)
    
    # Cluster formation using a stack-based method (LIFO)
    stack = [(x, y)]
    
    while stack:
        cx, cy = stack.pop()
        for nx, ny in neighbours(L, cx, cy):
            if (nx, ny) not in cluster_set and grid[nx, ny] == cluster_spin:
                if random.random() < prob_add:
                    cluster.append((nx, ny))
                    cluster_set.add((nx, ny))
                    stack.append((nx, ny))
    
    # Flip the entire cluster to a new spin state distinct from original
    new_spin = random.choice([s for s in range(q) if s != cluster_spin])
    for cx, cy in cluster:
        grid[cx, cy] = new_spin

    return len(cluster)

# Function to simulate the Potts model using Wolff's algorithm
def simulate_potts(L, q, beta, steps):
    """Simulates the Potts model using the Wolff cluster algorithm."""
    # Initialize the lattice with random q possible states
    grid = np.random.randint(0, q, (L, L))
    
    cluster_sizes = []
    
    plot_interval = max(steps // 10, 1)
    
    for step in range(steps):
        cluster_size = wolff_step(grid, beta, q)
        cluster_sizes.append(cluster_size)
        
        if step % plot_interval == 0:
            plt.imshow(grid, cmap='tab20')
            plt.title(f"Step {step}")
            plt.colorbar(label='Spin State')
            plt.show()
    
    return grid, cluster_sizes

if __name__ == "__main__":
    # Parameters
    L = 50    # Lattice dimensions
    q = 3     # Potts model states (q-state Potts model)
    beta = 0.6  # Inverse temperature (1/kT)
    steps = 1000  # Number of Monte Carlo iterations

    # Conduct the simulation
    final_grid, cluster_sizes = simulate_potts(L, q, beta, steps)

    # Plot cluster sizes over iterations
    plt.plot(cluster_sizes)
    plt.xlabel('Monte Carlo iteration')
    plt.ylabel('Cluster size')
    plt.title('Cluster sizes in Wolff simulation')
    plt.show()
