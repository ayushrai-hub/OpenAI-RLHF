# ideal_completion.py

import random
import numpy as np
from typing import Dict, List, Tuple, Optional

class ACOSolver:
    def __init__(self, venues: Dict, distances: Dict):
        # Initialize ACO Solver with venues and distances.
        if not venues:
            raise ValueError("Venues dictionary cannot be empty")
        if not distances:
            raise ValueError("Distances dictionary cannot be empty")
            
        self.venues = venues
        self.distances = distances
        self.pheromone = {}
        self._validate_input()
        self.initialize_pheromones()

    def _validate_input(self) -> None:
        # Validate input data for connectivity and completeness.
        # Check if all venues are reachable from depot
        for venue in self.venues:
            if (('W', venue) not in self.distances or 
                (venue, 'W') not in self.distances):
                raise ValueError(f"Venue {venue} not connected to depot")

        # Verify graph connectivity
        for v1 in list(self.venues.keys()) + ['W']:
            for v2 in list(self.venues.keys()) + ['W']:
                if v1 != v2:
                    # Check if there's either a direct path or path via depot
                    direct_path = (v1, v2) in self.distances
                    depot_path = ((v1, 'W') in self.distances and 
                                ('W', v2) in self.distances)
                    if not (direct_path or depot_path):
                        raise ValueError(f"No valid path between {v1} and {v2}")

    def initialize_pheromones(self, init_value: float = 0.1) -> None:
        # Initialize pheromone levels on all possible paths.
        self.pheromone = {}
        for v1 in list(self.venues.keys()) + ['W']:
            for v2 in list(self.venues.keys()) + ['W']:
                if v1 != v2:
                    self.pheromone[(v1, v2)] = init_value

    def calculate_expected_demand(self, venue: str) -> float:
        #Calculate expected demand for a venue."""
        if venue == 'W' or venue not in self.venues:
            return 0.0
        return float(np.average(self.venues[venue]['demand'], 
                              weights=self.venues[venue]['prob']))

    def get_path_distance(self, start: str, end: str) -> float:
            # Calculate the shortest path distance between two points.
            # Direct route distance
            direct_distance = self.distances.get((start, end), float('inf'))
            
            # Route through depot distance
            depot_distance = float('inf')
            if start != 'W' and end != 'W':
                to_depot = self.distances.get((start, 'W'), float('inf'))
                from_depot = self.distances.get(('W', end), float('inf'))
                if to_depot != float('inf') and from_depot != float('inf'):
                    depot_distance = to_depot + from_depot
            
            return min(direct_distance, depot_distance)

    def compute_route_distance(self, route: List[str]) -> float:
        # Compute the total distance of a route.
        if len(route) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(route) - 1):
            start, end = route[i], route[i + 1]
            leg_distance = self.get_path_distance(start, end)
            if leg_distance == float('inf'):
                raise ValueError(f"No valid path between {start} and {end}")
            total_distance += leg_distance
            
        return float(total_distance)
    def heuristic_prioritize_demand(self, loc1: str, loc2: str) -> float:
        # Calculate heuristic value combining demand and distance.
        if loc2 == 'W':
            return 0.0
        
        demand = self.calculate_expected_demand(loc2)
        distance = self.get_path_distance(loc1, loc2)
        
        if distance == float('inf'):
            return 0.0
            
        return float(demand / (distance + 1e-10))

    def solve(self, alpha: float = 1.0, beta: float = 2.0, rho: float = 0.5, 
             num_ants: int = 10, iterations: int = 100) -> Tuple[List[str], float]:
        # Solve the routing problem using ACO.
        # Validate parameters
        if alpha <= 0 or beta <= 0 or rho <= 0 or rho >= 1:
            raise ValueError("Invalid parameter values")
        if num_ants <= 0 or iterations <= 0:
            raise ValueError("Number of ants and iterations must be positive")

        venues_list = list(self.venues.keys())
        best_route: Optional[List[str]] = None
        best_distance = float('inf')
        
        # Sort venues by demand for initial guidance
        venue_demands = {v: self.calculate_expected_demand(v) for v in venues_list}
        sorted_venues = sorted(venues_list, key=lambda x: venue_demands[x], reverse=True)
        
        for _ in range(iterations):
            ant_routes: List[List[str]] = []
            ant_distances: List[float] = []
            
            for _ in range(num_ants):
                route = ['W']
                unvisited = set(venues_list)
                current = 'W'
                
                # Construct route prioritizing demand and distance
                while unvisited:
                    probabilities = []
                    for next_venue in unvisited:
                        tau = self.pheromone.get((current, next_venue), 0.1)
                        eta = self.heuristic_prioritize_demand(current, next_venue)
                        if eta > 0:
                            prob = (tau ** alpha) * (eta ** beta)
                            probabilities.append((next_venue, prob))
                    
                    if not probabilities:
                        # If no valid moves, choose closest unvisited venue
                        next_venue = min(unvisited, 
                                       key=lambda x: self.get_path_distance(current, x))
                    else:
                        total = sum(p for _, p in probabilities)
                        if total == 0:
                            next_venue = min(unvisited, 
                                           key=lambda x: self.get_path_distance(current, x))
                        else:
                            probabilities = [(v, p/total) for v, p in probabilities]
                            venues, probs = zip(*probabilities)
                            next_venue = random.choices(venues, weights=probs)[0]
                    
                    route.append(next_venue)
                    unvisited.remove(next_venue)
                    current = next_venue
                
                route.append('W')
                distance = self.compute_route_distance(route)
                ant_routes.append(route)
                ant_distances.append(distance)
                
                if distance < best_distance:
                    best_route = route
                    best_distance = distance
            
            # Update pheromones
            for key in self.pheromone:
                self.pheromone[key] *= (1 - rho)
            
            for route, distance in zip(ant_routes, ant_distances):
                deposit = 1.0 / distance
                for i in range(len(route) - 1):
                    self.pheromone[(route[i], route[i+1])] += deposit
        
        if best_route is None:
            raise RuntimeError("Failed to find valid route")
            
        return best_route, best_distance
