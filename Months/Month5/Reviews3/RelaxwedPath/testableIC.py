import random
import heapq
from typing import List, Tuple

class EnvAgent:
    def __init__(self, initial_position: Tuple[int, int], initial_direction: int, target: Tuple[int, int]) -> None:
        self.initial_position = initial_position
        self.initial_direction = initial_direction
        self.target = target

class Directions:
    NORTH, EAST, SOUTH, WEST = range(4)

class GridTransitionMap:
    def __init__(self, grid_size: Tuple[int, int]) -> None:
        self.grid_size = grid_size

    def get_transitions(self, x: int, y: int, direction: int) -> List[bool]:
        # Placeholder method that should be implemented
        pass

def bunny_heuristic(_rail, position: Tuple[int, int], target: Tuple[int, int]) -> int:
    return abs(position[0] - target[0]) + abs(position[1] - target[1])

def sipp(start: Tuple[int, int], target: Tuple[int, int], rail: GridTransitionMap, max_timestep: int, existing_paths: List[List[Tuple[int, int]]], direction: int) -> List[Tuple[int, int]]:
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

def handle_movement_sipp(loc: Tuple[int, int], g_cost: int, target: Tuple[int, int], path: List[Tuple[int, int]], open_list: List[Tuple[int, int, int, Tuple[int, int], List[Tuple[int, int]]]], rail: GridTransitionMap, existing_paths: List[List[Tuple[int, int]]], direction: int) -> None:
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

def is_conflict(new_loc: Tuple[int, int], new_g_cost: int, loc: Tuple[int, int], g_cost: int, existing_paths: List[List[Tuple[int, int]]]) -> bool:
    for path in existing_paths:
        if len(path) > new_g_cost:
            if path[new_g_cost] == new_loc:
                return True
            if path[new_g_cost] == loc and path[g_cost] == new_loc:
                return True
    return False

def replan(agents: List[EnvAgent], rail: GridTransitionMap, current_timestep: int, existing_paths: List[List[Tuple[int, int]]], max_timestep: int, new_malfunction_agents: List[int], failed_agents: List[int]) -> List[List[Tuple[int, int]]]:
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

def relaxed_planning(agents: List[EnvAgent], rail: GridTransitionMap, max_timestep: int, initial_planning_fraction: float) -> Tuple[List[List[Tuple[int, int]]], List[int]]:
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

def execute_with_relaxed_planning(agents: List[EnvAgent], rail: GridTransitionMap, max_timestep: int, initial_planning_fraction: float) -> List[List[Tuple[int, int]]]:
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
