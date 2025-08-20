# utils.py
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
 