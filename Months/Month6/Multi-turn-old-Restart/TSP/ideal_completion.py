import random
from functools import lru_cache
import itertools
from concurrent.futures import ThreadPoolExecutor

def tournament_selection(population, fitness, tournament_size=5):
    tournament = random.sample(list(zip(population, fitness)), tournament_size)
    tournament.sort(key=lambda x: x[1])
    return tournament[0][0]

def ordered_crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size

    child[start:end+1] = parent1[start:end+1]

    p2_current = 0
    for i in range(size):
        if child[i] is None:
            while parent2[p2_current] in child:
                p2_current += 1
            child[i] = parent2[p2_current]

    return child

def mutate(route, mutation_rate=0.01):
    route = route[:]
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

def held_karp(distance_matrix):
    n = len(distance_matrix)

    @lru_cache(maxsize=None)
    def visit(mask, pos):
        if mask == (1 << n) - 1:
            return distance_matrix[pos][0]
        min_cost = float('inf')
        for city in range(n):
            if mask & (1 << city) == 0:
                cost = distance_matrix[pos][city] + visit(mask | (1 << city), city)
                if cost < min_cost:
                    min_cost = cost
        return min_cost

    return visit(1, 0)

def parallel_evaluate(population, fitness_func):
    with ThreadPoolExecutor() as executor:
        fitness = list(executor.map(fitness_func, population))
    return fitness

def route_distance(route, distance_matrix):
    distance = 0
    for i in range(len(route)):
        distance += distance_matrix[route[i]][route[(i + 1) % len(route)]]
    return distance
