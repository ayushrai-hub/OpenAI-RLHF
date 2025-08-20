import random
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from typing import List, Tuple, Dict, Any, Union
from matplotlib.figure import Figure as MatplotlibFigure
from plotly.graph_objs._figure import Figure as PlotlyFigure

from utils import (
    compute_total_metal,
    assess_airflow_difference,
    evaluate_violations,
    generate_random_individual,
    randomize_route_or_riser,
    room_info
)

def initialize_population(pop_size: int, room_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    population = []
    for _ in range(pop_size):
        individual = generate_random_individual(room_info)
        population.append(individual)
    return population

def calculate_fitness(individual: Dict[str, Any]) -> int:
    total_metal = compute_total_metal(individual)
    airflow_diff = assess_airflow_difference(individual)
    violations = evaluate_violations(individual)
    fitness = total_metal + airflow_diff * 1000 + violations * 10000
    return fitness

def crossover(parent1: List[Any], parent2: List[Any]) -> Tuple[List[Any], List[Any]]:
    crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
    return offspring1, offspring2

def mutate(individual: List[Any]) -> List[Any]:
    mutated_individual = individual.copy()
    if mutated_individual:
        mutation_index = random.randint(0, len(mutated_individual) - 1)
        mutated_individual[mutation_index] = randomize_route_or_riser(mutated_individual[mutation_index])
    return mutated_individual

def visualize_ductwork(solution: Dict[str, Any]) -> MatplotlibFigure:
    fig, ax = plt.subplots()
    for route in solution.get("routes", []):
        points = route.get("points", [])
        x_vals, y_vals = zip(*[(point["x"], point["y"]) for point in points])
        ax.plot(x_vals, y_vals, marker="o")
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_title('2D Ductwork Visualization')
    ax.grid(True)
    return fig

def visualize_ductwork_3D(solution: Dict[str, Any]) -> PlotlyFigure:
    fig = go.Figure()
    for route in solution.get("routes", []):
        points = route.get("points", [])
        x_vals = [point["x"] for point in points]
        y_vals = [point["y"] for point in points]
        z_vals = [max(3000, point.get("z", 3000)) for point in points]
        fig.add_trace(go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode="lines+markers"))
    fig.update_layout(
        title="3D Ductwork Visualization",
        scene=dict(
            xaxis_title="X Position (mm)",
            yaxis_title="Y Position (mm)",
            zaxis_title="Elevation (mm)",
            aspectmode="auto"
        )
    )
    return fig

def export_to_json(best_solution: Dict[str, Any], file_path: str) -> str:
    json_data = json.dumps(best_solution, indent=4)
    with open(file_path, 'w') as json_file:
        json_file.write(json_data)
    return json_data
