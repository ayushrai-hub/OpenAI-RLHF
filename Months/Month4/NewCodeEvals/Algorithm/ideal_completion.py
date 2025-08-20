import random
import numpy as np

# Fixed random seed for reproducibility
random.seed(42)

# Venues with demands, probabilities, and distances
venues = {
    'A': {'demand': [50, 70], 'prob': [0.4, 0.6]},
    'B': {'demand': [40, 60], 'prob': [0.3, 0.7]},
    'C': {'demand': [70, 100], 'prob': [0.3, 0.7]},
    'D': {'demand': [30, 50], 'prob': [0.4, 0.6]},
    'W': {}  # Depot doesn't have demand
}

# Distances between locations (bidirectional)
distances = {
    ('W', 'A'): 5, ('A', 'W'): 5,
    ('W', 'B'): 10, ('B', 'W'): 10,
    ('W', 'C'): 12, ('C', 'W'): 12,
    ('W', 'D'): 2, ('D', 'W'): 2,
    ('A', 'B'): 6, ('B', 'A'): 6,
    ('A', 'C'): float('inf'), ('C', 'A'): float('inf'),  # No direct path
    ('A', 'D'): 8, ('D', 'A'): 8,
    ('B', 'C'): 4, ('C', 'B'): 4,
    ('B', 'D'): float('inf'), ('D', 'B'): float('inf'),  # No direct path
    ('C', 'D'): 6, ('D', 'C'): 6
}

# Function to calculate expected demand
def calculate_expected_demand(venue):
    return np.average(venues[venue]['demand'], weights=venues[venue]['prob'])

# Compute route distance
def compute_route_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        dist = distances.get((route[i], route[i+1]), float('inf'))
        # If no direct path, go via depot
        if dist == float('inf'):
            dist = distances.get((route[i], 'W'), float('inf')) + distances.get(('W', route[i+1]), float('inf'))
        total_distance += dist
    return total_distance

# Heuristic function that prioritizes demand and distance
def heuristic_prioritize_demand(loc1, loc2):
    demand = calculate_expected_demand(loc2)
    distance = distances.get((loc1, loc2), float('inf'))
    # If no direct path, consider distance via depot
    if distance == float('inf'):
        distance = distances.get((loc1, 'W'), float('inf')) + distances.get(('W', loc2), float('inf'))
    return demand / (distance + 1e-10)  # Avoid division by zero

# Ant Colony Optimization algorithm

def aco_solver(alpha=1.0, beta=2.0, rho=0.5, pheromone_init=0.1, num_ants=10, iterations=100):
    random.seed(42)  # Control randomness
    venues_list = ['A', 'B', 'C', 'D']

    # Initialize pheromone levels on all edges
    pheromone = {}
    all_edges = set()
    for loc1 in venues_list + ['W']:
        for loc2 in venues_list + ['W']:
            if loc1 != loc2 and ((loc1, loc2) in distances or (loc1, 'W') in distances and ('W', loc2) in distances):
                pheromone[(loc1, loc2)] = pheromone_init
                all_edges.add((loc1, loc2))
    best_route = None
    best_distance = float('inf')

    for iteration in range(iterations):
        random.seed(42 + iteration)  # Different seed per iteration
        all_routes = []
        all_distances = []
        
        for ant in range(num_ants):
            # Initialize starting point
            route = ['W']
            unvisited = set(venues_list)
            
            while unvisited:
                current_loc = route[-1]
                probabilities = []
                # Calculate probabilities for next move
                for next_loc in unvisited:
                    tau = pheromone.get((current_loc, next_loc), pheromone_init)
                    eta = heuristic_prioritize_demand(current_loc, next_loc)
                    prob = (tau ** alpha) * (eta ** beta)
                    probabilities.append((next_loc, prob))
                # Normalize probabilities
                total = sum(prob for _, prob in probabilities)
                if total == 0:
                    # If all probabilities are zero, choose randomly
                    next_loc = random.choice(list(unvisited))
                else:
                    probabilities = [(loc, prob / total) for loc, prob in probabilities]
                    # Choose next location based on probabilities
                    locs = [loc for loc, _ in probabilities]
                    probs = [prob for _, prob in probabilities]
                    next_loc = random.choices(locs, probs)[0]
                route.append(next_loc)
                unvisited.remove(next_loc)
            route.append('W')  # Return to depot
            total_distance = compute_route_distance(route)
            all_routes.append(route)
            all_distances.append(total_distance)
            if total_distance < best_distance:
                best_route = route
                best_distance = total_distance
        # Pheromone evaporation
        for edge in all_edges:
            pheromone[edge] *= (1 - rho)
        # Update pheromones based on routes
        for route, distance in zip(all_routes, all_distances):
            increase = 1.0 / distance
            for i in range(len(route) - 1):
                edge = (route[i], route[i+1])
                pheromone[edge] += increase
    return best_route, best_distance

# Example execution
if __name__ == "__main__":
    best_route, best_distance = aco_solver()
    print(f"ACO Best Route: {best_route}")
    print(f"ACO Total Distance: {best_distance}")