import unittest
import json
import random
from matplotlib.figure import Figure
from plotly.graph_objects import Figure as PlotlyFigure
import os

# Creating utils file with functions needed to run the ideal completion
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "utils.py")), 'w') as file:
            file.write("""# utils.py
import random

def compute_total_metal(individual):
    total_metal = sum(duct['length'] for duct in individual['ducts'])
    return total_metal

def assess_airflow_difference(individual):
    ideal_airflow = 100
    actual_airflow = sum(duct['airflow'] for duct in individual['ducts'])
    airflow_deviation = abs(ideal_airflow - actual_airflow)
    return airflow_deviation

def evaluate_violations(individual):
    penalty = 0
    for duct in individual['ducts']:
        if duct['length'] > 50:
            penalty += 10
    return penalty

def generate_random_individual(room_info):
    num_ducts = random.randint(1, 10)
    individual = {
        'ducts': [{'id': i, 'length': random.uniform(5, 50), 'airflow': random.uniform(10, 30),
                   'coordinates': [(random.randint(0, room_info['width']), random.randint(0, room_info['height'])) 
                                   for _ in range(2)]} 
                  for i in range(num_ducts)],
        'risers': [(random.randint(0, room_info['width']), random.randint(0, room_info['height'])) 
                   for _ in range(5)]
    }
    return individual

def randomize_route_or_riser(route_or_riser):
    if isinstance(route_or_riser, dict) and 'coordinates' in route_or_riser:
        route_or_riser['coordinates'] = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(2)]
    elif isinstance(route_or_riser, tuple) and len(route_or_riser) == 2:
        route_or_riser = (random.randint(0, 100), random.randint(0, 100))
    return route_or_riser

room_info = {
    'width': 100,
    'height': 100,
    'depth': 50
}
 """)

from utils import generate_random_individual, room_info 
from ideal_completion import (
    calculate_fitness,
    initialize_population,
    crossover,
    mutate,
    visualize_ductwork,
    visualize_ductwork_3D,
    export_to_json
)

class testIdealCompletion(unittest.TestCase):


    # Testing calculate fitsness function to ensure it returns the expected type 
    # of values.
    def test_calculate_fitness(self):
        # Example individual for testing
        individual = generate_random_individual(room_info)
        fitness = calculate_fitness(individual)
        self.assertIsInstance(fitness, (int, float))

    # Testing initialize_population function to ensure it returns the expected 
    # amount of individuals
    def test_initialize_population(self):
        room_info_sample = {'width': 100, 'height': 100, 'depth': 50}
        population = initialize_population(10, room_info_sample)
        self.assertEqual(len(population), 10)
        self.assertIsInstance(population, list)

    # Testing crossover function to ensure it returns the expected result
    def test_crossover(self):
        parent1 = [1, 2, 3, 4, 5]
        parent2 = [5, 4, 3, 2, 1]
        offspring1, offspring2 = crossover(parent1, parent2)
        self.assertEqual(len(offspring1), len(parent1))
        self.assertEqual(len(offspring2), len(parent2))
        self.assertNotEqual(offspring1, parent1)
        self.assertNotEqual(offspring2, parent2)

    # Testing mutate function to ensure it won't alter the `individual` length
    def test_mutate(self):
        individual = [1, 2, 3, 4, 5]
        mutated = mutate(individual.copy())
        self.assertEqual(len(mutated), len(individual))

    # Testing visualize_ductwork function to ensure it returns the expected type 
    # in the result
    def test_visualize_ductwork(self):
        solution = {'ducts': [{'id': 1, 'coordinates': [(0, 0), (1, 1)]}], 'risers': [[0, 0], [1, 1]]}
        fig = visualize_ductwork(solution)
        self.assertIsInstance(fig, Figure)

    # Testing visualize_ductwork_3D function to ensure it returns the expected type
    def test_visualize_ductwork_3D(self):
        solution = {
            'ducts': [{'id': 1, 'coordinates': [(0, 0, 0), (1, 1, 1)]}],
            'risers': [[0, 0, 0], [1, 1, 1]]
        }
        fig = visualize_ductwork_3D(solution)
        self.assertIsInstance(fig, PlotlyFigure)

    # Testing export_to_json function to ensure it returns the expected type
    # and best solution possible.
    def test_export_to_json(self):
        best_solution = {'example_key': 'example_value'}
        json_data = export_to_json(best_solution, 'output.json')
        self.assertIsInstance(json_data, str)
        self.assertEqual(json.loads(json_data), best_solution)

if __name__ == '__main__':
    unittest.main(verbosity=2)