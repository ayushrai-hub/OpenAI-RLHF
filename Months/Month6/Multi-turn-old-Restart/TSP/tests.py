import unittest
import ideal_completion
import random

class TestTSPAlgorithm(unittest.TestCase):

    # Test to check  correct selection of the best individual
    # This is important because it ensures that the selection process is actually biased towards ideals.
    def test_tournament_selection(self):
        population = [[0, 1, 2], [1, 0, 2], [2, 0, 1], [1, 2, 0], [2, 1, 0]]
        fitness = [10, 20, 30,40,50]
        result = ideal_completion.tournament_selection(population, fitness)
        self.assertEqual(result, [0, 1, 2])

    # Test to check ordered crossover confirming that the  offsprings have the correct elements from parents.
    # Its important to make sure that the genetic material from both parent is correctly combined without duplicates.
    def test_ordered_crossover(self):
        parent1 = [1, 2, 3, 4]
        parent2 = [4, 3, 2, 1]
        child = ideal_completion.ordered_crossover(parent1, parent2)
        self.assertEqual(set(child), set([1, 2, 3, 4]))

    # Test to check mutation function to verify changes mutation when rate is very high
    # Its important for verifying genetic diversity as the  mutation should output a different route.
    def test_mutate(self):
        route = [1, 2, 3, 4]
        mutated_route = ideal_completion.mutate(route.copy(), mutation_rate=1.0)
        self.assertNotEqual(mutated_route, route)
  
    # Test to check mutation function to verify changes mutation when rate is very low
    # Its important for verifying genetic diversity as the  mutation should output a different route.
    def test_low_mutation_rate(self):
        random.seed(0)  # Set seed for reproducibility
        route = [1, 2, 3, 4]
        mutated_route = ideal_completion.mutate(route.copy(), mutation_rate=0.001)
        self.assertEqual(mutated_route, route)

    # Test to run Held-Karp function for a simple 4-city problem
    # Its important as it verifies the  TSP path length for a known solution, confirming DP implementation is correct
    def test_held_karp(self):
        cities = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]
        result = ideal_completion.held_karp(cities)
        self.assertEqual(result, 80)

    # Test to run tha parallel fitness evaluation to make sure  it evaluates all individuals correctly
    #Its important to evaluate  performance with large populations, checking fitness is calculated without errors.
    def test_parallel_evaluate(self):
        population = [[0, 1, 2], [1, 0, 2], [2, 1, 0]]
        def fitness_func(route):
            return sum(route)  
        fitness = ideal_completion.parallel_evaluate(population, fitness_func)
        self.assertEqual(fitness, [3, 3, 3])

  

if __name__ == '__main__':
    unittest.main(verbosity=2)

