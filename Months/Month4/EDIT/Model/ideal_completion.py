# ideal_completion.py

import heapq
from typing import List, Tuple

class Directions:
    NORTH, EAST, SOUTH, WEST = range(4)

class EnvAgent:
    def __init__(self, initial_position, initial_direction, target):
        self.initial_position = initial_position
        self.initial_direction = initial_direction
        self.target = target
        self.position = initial_position
        self.direction = initial_direction

def bunny_heuristic(rail, position, target):
    # Use Manhattan distance as heuristic
    return abs(position[0] - target[0]) + abs(position[1] - target[1])

def sipp(start, target, rail, max_timestep, existing_paths, direction):
    """
    Safe Interval Path Planning (SIPP) to find a collision-free path from start to target.
    """
    open_list = []
    heapq.heappush(open_list, (bunny_heuristic(rail, start, target), 0, start, direction, []))
    visited = set()

    while open_list:
        f_cost, g_cost, current_loc, current_direction, path = heapq.heappop(open_list)

        if current_loc == target:
            return path + [current_loc]

        if (current_loc, g_cost) in visited:
            continue
        visited.add((current_loc, g_cost))

        # Explore neighbors and handle movement using SIPP
        handle_movement_sipp(current_loc, g_cost, target, path, open_list, rail, existing_paths,
                             current_direction, max_timestep)

    return []  # Return empty path if no path is found

def handle_movement_sipp(loc, g_cost, target, path, open_list, rail, existing_paths, direction, max_timestep):
    """
    Handles movement using Safe Interval Path Planning (SIPP) by exploring valid transitions.
    """
    if g_cost >= max_timestep:
        return

    valid_transitions = rail.get_transitions(loc[0], loc[1], direction)

    for new_direction, is_valid in enumerate(valid_transitions):
        if is_valid:
            new_x, new_y = loc

            # Update the location based on the new direction
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

            # Check for conflicts with existing paths
            if not is_conflict(new_loc, new_g_cost, loc, g_cost, existing_paths):
                new_f_cost = new_g_cost + bunny_heuristic(rail, new_loc, target)
                heapq.heappush(open_list, (new_f_cost, new_g_cost, new_loc, new_direction, path + [loc]))

def is_conflict(new_loc, new_g_cost, loc, g_cost, existing_paths):
    """
    Checks for conflicts with other agents' paths.
    """
    for path in existing_paths:
        if len(path) > new_g_cost:
            # Vertex conflict
            if path[new_g_cost] == new_loc:
                return True
            # Edge conflict
            if path[new_g_cost - 1] == new_loc and path[new_g_cost] == loc:
                return True
    return False

def relaxed_planning(agents: List[EnvAgent], rail, max_timestep: int, initial_planning_fraction: float):
    """
    Performs relaxed path planning where only a fraction of agents are planned initially,
    and others are planned dynamically during execution.
    """
    total_agents = len(agents)
    initial_agents = int(total_agents * initial_planning_fraction)
    path_compendium = []  # Paths for all agents
    existing_paths = []   # Paths that are already planned
    pending_agents = []   # Agents pending planning

    # Plan paths for the initial set of agents
    for agent_id, agent in enumerate(agents):
        if agent_id < initial_agents:
            start = agent.initial_position
            start_direction = agent.initial_direction
            target = agent.target

            # Plan path using SIPP
            path = sipp(start, target, rail, max_timestep, existing_paths, start_direction)
            path_compendium.append(path)
            existing_paths.append(path)
        else:
            # Agent is pending planning
            path_compendium.append([])
            pending_agents.append(agent_id)

    return path_compendium, pending_agents

def execute_with_relaxed_planning(agents: List[EnvAgent], rail, max_timestep: int, initial_planning_fraction: float):
    """
    Executes the simulation using relaxed planning, where only a fraction of paths are planned initially,
    and others are planned dynamically as needed during execution.
    """
    # Initial relaxed planning
    path_compendium, pending_agents = relaxed_planning(agents, rail, max_timestep, initial_planning_fraction)
    existing_paths = [path for path in path_compendium if path]

    # Simulate movements for each timestep
    for timestep in range(max_timestep):
        # Move agents that have paths
        for agent_id, path in enumerate(path_compendium):
            if path and len(path) > timestep:
                # Update agent's position
                agents[agent_id].position = path[timestep]

        # Plan for pending agents
        new_pending_agents = []
        for agent_id in pending_agents:
            agent = agents[agent_id]
            current_timestep = timestep
            current_position = agent.position if timestep > 0 else agent.initial_position
            current_direction = agent.direction
            target = agent.target

            # Plan path from current position
            remaining_timesteps = max_timestep - current_timestep
            path = sipp(current_position, target, rail, remaining_timesteps, existing_paths, current_direction)

            if path:
                # Adjust the path to include the time steps passed
                full_path = [current_position] * current_timestep + path
                path_compendium[agent_id] = full_path
                existing_paths.append(full_path)
            else:
                # Could not find a path, try again in next timestep
                new_pending_agents.append(agent_id)
        pending_agents = new_pending_agents

    return path_compendium