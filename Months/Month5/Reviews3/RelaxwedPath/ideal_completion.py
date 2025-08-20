# ideal_completion.py
import random
import heapq
from typing import List, Tuple 

class EnvAgent:
    def __init__(self, initial_position, initial_direction, target):
        self.initial_position = initial_position
        self.initial_direction = initial_direction
        self.target = target

class Directions:
    # Direction indices for transitioning between cells in the grid
    NORTH, EAST, SOUTH, WEST = range(4)

class GridTransitionMap:
    def __init__(self, grid_size: Tuple[int, int]):
        self.grid_size = grid_size
        self.directions = {
            Directions.NORTH: (-1, 0),
            Directions.EAST: (0, 1),
            Directions.SOUTH: (1, 0),
            Directions.WEST: (0, -1),
        }

    def get_transitions(self, x: int, y: int, direction: int) -> List[bool]:
        valid_transitions = [False] * 4  # [NORTH, EAST, SOUTH, WEST]
        
        if x > 0:
            valid_transitions[Directions.NORTH] = True
        if y < self.grid_size[1] - 1:
            valid_transitions[Directions.EAST] = True
        if x < self.grid_size[0] - 1:
            valid_transitions[Directions.SOUTH] = True
        if y > 0:
            valid_transitions[Directions.WEST] = True

        return valid_transitions

def bunny_heuristic(_rail, position, target):
    return abs(position[0] - target[0]) + abs(position[1] - target[1])

def sipp(start, target, rail, max_timestep, existing_paths, direction):
    """
    Safe Interval Path Planning (SIPP) to discover a collision-free route from start to target.
    """
    open_list = []
    heapq.heappush(open_list, (0 + bunny_heuristic(None, start, target), 0, start, direction, []))
    visited = set()

    while open_list:
        f_cost, g_cost, current_loc, current_direction, path = heapq.heappop(open_list)

        if current_loc == target:
            return path + [current_loc]

        if (current_loc, g_cost) in visited:
            continue
        visited.add((current_loc, g_cost))

        handle_movement_sipp(current_loc, g_cost, target, path, open_list, rail, existing_paths, current_direction)

    return []

def handle_movement_sipp(loc, g_cost, target, path, open_list, rail, existing_paths, direction):
    """
    Manages movement using Safe Interval Path Planning (SIPP) by examining valid transitions.
    """
    valid_transitions = rail.get_transitions(loc[0], loc[1], direction)

    for i, is_valid in enumerate(valid_transitions):
        if is_valid:
            new_x, new_y = loc
            new_direction = i

            if new_direction == Directions.NORTH:
                new_x -= 1
            elif new_direction == Directions.EAST:
                new_y += 1
            elif new_direction == Directions.SOUTH:
                new_x += 1
            elif new_direction == Directions.WEST:
                new_y -= 1

            new_loc = (new_x, new_y)
            new_g_cost = g_cost + 1

            if not is_conflict(new_loc, new_g_cost, loc, g_cost, existing_paths):
                new_f_cost = new_g_cost + bunny_heuristic(None, new_loc, target)
                heapq.heappush(open_list, (new_f_cost, new_g_cost, new_loc, new_direction, path + [loc]))

def is_conflict(new_loc, new_g_cost, loc, g_cost, existing_paths):
    """
    Validate conflicts with other agents' routes.
    """
    for path in existing_paths:
        if len(path) > new_g_cost:
            if path[new_g_cost] == new_loc:
                return True
            if path[new_g_cost] == loc and path[g_cost] == new_loc:
                return True
    return False

def replan(agents, rail, current_timestep, existing_paths, max_timestep, new_malfunction_agents, failed_agents):
    """
    Replan paths for agents experiencing malfunctions or unable to adhere to their plotted route.
    """

    # Replan for agents affected by malfunctions and failed agents
    agents_to_replan = set(new_malfunction_agents + failed_agents)

    for agent_id in agents_to_replan:
        agent = agents[agent_id]
        current_loc = existing_paths[agent_id][current_timestep]
        current_direction = agent.initial_direction
        target = agent.target

        existing_paths[agent_id] = existing_paths[agent_id][:current_timestep]

        new_path = sipp(current_loc, target, rail, max_timestep, existing_paths, current_direction)

        if new_path:
            existing_paths[agent_id].extend(new_path)

    return existing_paths

def relaxed_planning(agents, rail, max_timestep, initial_planning_fraction):
    """
    Facilitates relaxed path planning where only a portion of agents' routes are planned initially,
    with future routes planned dynamically during execution.
    """
    total_agents = len(agents)
    initial_agents = int(total_agents * initial_planning_fraction)

    path_compendium = []
    ongoing_paths = []
    pending_agents = []

    for agent_id, agent in enumerate(agents):
        if agent_id < initial_agents:
            start = agent.initial_position
            start_direction = agent.initial_direction
            dest = agent.target
            path = sipp(start, dest, rail, max_timestep, ongoing_paths, start_direction)
            path_compendium.append(path)
            ongoing_paths.append(path)
        else:
            pending_agents.append(agent_id)
            path_compendium.append([])

    return path_compendium, pending_agents

def execute_with_relaxed_planning(agents, rail, max_timestep, initial_planning_fraction):
    """
    Carries out the simulation using relaxed planning, where only a partial set of routes are initially planned,
    and others are planned adaptively as needed during execution.
    """
    path_compendium, pending_agents = relaxed_planning(agents, rail, max_timestep, initial_planning_fraction)

    for timestep in range(max_timestep):
        for agent_id, path in enumerate(path_compendium):
            if path and len(path) > timestep:
                pass

        for agent_id in pending_agents:
            agent = agents[agent_id]
            present_loc = agent.initial_position if timestep == 0 else path_compendium[agent_id][timestep - 1]
            current_direction = agent.initial_direction
            dest = agent.target

            new_route = sipp(present_loc, dest, rail, max_timestep, path_compendium, current_direction)
            path_compendium[agent_id] = new_route
            pending_agents.remove(agent_id)

        malfunctioning_agents = []
        failed_agents = []
        if malfunctioning_agents or failed_agents:
            path_compendium = replan(agents, rail, timestep, path_compendium, max_timestep, malfunctioning_agents, failed_agents)

    return path_compendium

# Run a sample simulation
agents = [
    EnvAgent(initial_position=(0, 0), initial_direction=Directions.EAST, target=(5, 5)),
    EnvAgent(initial_position=(1, 1), initial_direction=Directions.SOUTH, target=(4, 4)),
]

grid_size = (6, 6)
rail = GridTransitionMap(grid_size)
max_timestep = 10
initial_planning_fraction = 0.5

final_paths = execute_with_relaxed_planning(agents, rail, max_timestep, initial_planning_fraction)

# Output the final paths for each agent
for agent_id, path in enumerate(final_paths):
    print(f"Agent {agent_id} path: {path}")