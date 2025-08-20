
import unittest
import random
import numpy as np
from typing import Dict, List
from parameterized import parameterized
import time
from new_ideal_completion import ACOSolver
class TestACOSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize test data and solver instance.
        # Set fixed seeds for reproducibility
        random.seed(42)
        np.random.seed(42)
        
        cls.test_venues = {
            'A': {'demand': [50, 70], 'prob': [0.4, 0.6]},
            'B': {'demand': [40, 60], 'prob': [0.3, 0.7]},
            'C': {'demand': [70, 100], 'prob': [0.3, 0.7]},
            'D': {'demand': [30, 50], 'prob': [0.4, 0.6]}
        }
        
        cls.test_distances = {
            ('W', 'A'): 5, ('A', 'W'): 5,
            ('W', 'B'): 10, ('B', 'W'): 10,
            ('W', 'C'): 12, ('C', 'W'): 12,
            ('W', 'D'): 2, ('D', 'W'): 2,
            ('A', 'B'): 6, ('B', 'A'): 6,
            ('A', 'D'): 8, ('D', 'A'): 8,
            ('B', 'C'): 4, ('C', 'B'): 4,
            ('C', 'D'): 6, ('D', 'C'): 6
        }
        
        cls.solver = ACOSolver(cls.test_venues, cls.test_distances)
        
        cls.expected_demands = {
            'A': 62.0,  # 50*0.4 + 70*0.6
            'B': 54.0,  # 40*0.3 + 60*0.7
            'C': 91.0,  # 70*0.3 + 100*0.7
            'D': 42.0,  # 30*0.4 + 50*0.6
            'W': 0.0
        }

    def setUp(self):
        # Reset solver state before each test.
        self.solver.initialize_pheromones()

    def tearDown(self):
        # Clean up after each test.
        pass

    def test_initialization(self):
        # Test solver initialization and validation.
        # Test valid initialization
        solver = ACOSolver(self.test_venues, self.test_distances)
        self.assertIsInstance(solver.venues, dict)
        self.assertIsInstance(solver.distances, dict)
        
        # Test empty venues
        with self.assertRaises(ValueError):
            ACOSolver({}, self.test_distances)
        
        # Test empty distances
        with self.assertRaises(ValueError):
            ACOSolver(self.test_venues, {})
        
        # Test disconnected graph
        invalid_distances = self.test_distances.copy()
        del invalid_distances[('W', 'A')]
        with self.assertRaises(ValueError):
            ACOSolver(self.test_venues, invalid_distances)

    @parameterized.expand([
        ('A', 62.0), ('B', 54.0), ('C', 91.0), ('D', 42.0),
        ('W', 0.0), ('X', 0.0)
    ])
    def test_calculate_expected_demand(self, venue, expected):
        # Test demand calculation for various venues.
        demand = self.solver.calculate_expected_demand(venue)
        self.assertIsInstance(demand, float)
        self.assertEqual(demand, expected)

    def test_get_path_distance(self):
        # Test individual path distance calculations.
        test_cases = [
            # Direct routes
            (('W', 'A'), 5),  # Direct from depot to A
            (('A', 'B'), 6),  # Direct A to B
            
            # Routes requiring depot
            (('A', 'C'), 17),  # A->W->C = 5 + 12
            (('B', 'D'), 12),  # B->W->D = 10 + 2
            
            # Non-existent direct routes
            (('X', 'Y'), float('inf')),  # Invalid locations
        ]
        
        for (start, end), expected in test_cases:
            distance = self.solver.get_path_distance(start, end)
            self.assertEqual(distance, expected, 
                            f"Incorrect distance from {start} to {end}")

    def test_compute_route_distance(self):
        """Test complete route distance computation."""
        test_routes = [
            # Simple direct route
            (['W', 'A', 'W'], 10),  # 5 + 5
            
            # Route with direct connections
            (['W', 'A', 'B', 'W'], 21),  # 5 + 6 + 10
            
            # Route requiring depot transit
            (['W', 'A', 'C', 'W'], 34.0), 
            
            # Complex mixed route
            (['W', 'D', 'C', 'B', 'A', 'W'], 23),  # 2 + 6 + 4 + 6 + 5
        ]
        
        for route, expected in test_routes:
            distance = self.solver.compute_route_distance(route)
            self.assertEqual(distance, expected, 
                            f"Incorrect distance for route {route}. "
                            f"Got {distance}, expected {expected}")

        # Test empty and single-point routes
        self.assertEqual(self.solver.compute_route_distance([]), 0.0)
        self.assertEqual(self.solver.compute_route_distance(['W']), 0.0)
        
        # Test invalid route
        with self.assertRaises(ValueError):
            self.solver.compute_route_distance(['W', 'X', 'Y'])

    def test_solve_basic_functionality(self):
        """Test basic solving functionality."""
        route, distance = self.solver.solve(iterations=10)
        
        # Verify route format
        self.assertEqual(route[0], 'W')
        self.assertEqual(route[-1], 'W')
        self.assertEqual(len(set(route[1:-1])), len(self.test_venues))
        
        # Verify distance
        self.assertGreater(distance, 0)
        self.assertTrue(np.isfinite(distance))



    def test_demand_tie_breaking(self):
        # Test tie-breaking with equal demands.
        # Create test case with equal demands
        equal_venues = {
            'A': {'demand': [50, 50], 'prob': [0.5, 0.5]},
            'B': {'demand': [50, 50], 'prob': [0.5, 0.5]}
        }
        equal_distances = {
            ('W', 'A'): 5, ('A', 'W'): 5,
            ('W', 'B'): 10, ('B', 'W'): 10,
            ('A', 'B'): 15, ('B', 'A'): 15  # Make direct route expensive
        }
        
        solver = ACOSolver(equal_venues, equal_distances)
        route, _ = solver.solve(iterations=20, beta=5.0)
        venues = [v for v in route if v != 'W']
        
        # A should be visited first as it's closer to depot with equal demand
        self.assertEqual(venues[0], 'A', 
                       "Should visit closer venue first when demands are equal")

    def test_path_selection(self):
        # Test optimal path selection.
        # Create test case where path via depot is shorter
        modified_distances = self.test_distances.copy()
        modified_distances[('A', 'B')] = 20  # Direct route
        modified_distances[('B', 'A')] = 20  # Make direct route expensive
        
        solver = ACOSolver(self.test_venues, modified_distances)
        route, distance = solver.solve(iterations=20, beta=5.0)
        
        # Calculate cost of direct path vs depot path
        direct_cost = modified_distances[('A', 'B')]
        depot_cost = (modified_distances[('A', 'W')] + 
                     modified_distances[('W', 'B')])
        
        self.assertLess(depot_cost, direct_cost, 
                       "Path through depot should be shorter")
        self.assertLess(distance, direct_cost * len(self.test_venues), 
                       "Solution should prefer shorter paths")

    def test_error_handling(self):
        # Test error handling for invalid inputs and edge cases.
        # Test invalid parameters
        with self.assertRaises(ValueError):
            self.solver.solve(alpha=-1.0)
        with self.assertRaises(ValueError):
            self.solver.solve(beta=0.0)
        with self.assertRaises(ValueError):
            self.solver.solve(rho=1.5)
        with self.assertRaises(ValueError):
            self.solver.solve(num_ants=0)
        with self.assertRaises(ValueError):
            self.solver.solve(iterations=0)
            
        # Test invalid graph structure
        disconnected_distances = self.test_distances.copy()
        for key in list(disconnected_distances.keys()):
            if 'A' in key:
                del disconnected_distances[key]
                
        with self.assertRaises(ValueError):
            ACOSolver(self.test_venues, disconnected_distances)
            
        # Test empty inputs
        with self.assertRaises(ValueError):
            ACOSolver({}, self.test_distances)
        with self.assertRaises(ValueError):
            ACOSolver(self.test_venues, {})

 

    def test_pheromone_updates(self):
        # Test pheromone update mechanism.
        initial_pheromones = self.solver.pheromone.copy()
        
        # Run solver for one iteration
        self.solver.solve(iterations=1, num_ants=1)
        
        # Verify pheromone changes
        changed_values = False
        for key in self.solver.pheromone:
            if self.solver.pheromone[key] != initial_pheromones[key]:
                changed_values = True
                break
        
        self.assertTrue(changed_values, 
                       "Pheromone levels should update during solving")
        
        # Verify pheromone values remain non-negative
        for value in self.solver.pheromone.values():
            self.assertGreaterEqual(value, 0, 
                                  "Pheromone values should never be negative")

    def test_performance(self):
        # Test solver performance and timeout.
        start_time = time.time()
        
        try:
            route, distance = self.solver.solve(iterations=50)
            end_time = time.time()
            
            # Check execution time
            execution_time = end_time - start_time
            self.assertLess(execution_time, 5.0, 
                          "Solver should complete within reasonable time")
            
            # Verify solution quality
            self.assertTrue(len(route) >= len(self.test_venues) + 2, 
                          "Route should visit all venues")
            self.assertGreater(distance, 0, 
                             "Distance should be positive")
            
        except Exception as e:
            self.fail(f"Solver failed performance test: {str(e)}")

if __name__ == '__main__':
    unittest.main(verbosity=2)