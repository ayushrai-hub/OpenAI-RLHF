#ideal_completion
import sys
from collections import deque
import heapq
import datetime

def read_puzzle(file_path):
    with open(file_path, 'r') as file:
        puzzle = [list(map(int, line.split())) for line in file]
    return puzzle

def find_blank(puzzle):
    for i, row in enumerate(puzzle):
        for j, value in enumerate(row):
            if value == 0:
                return (i, j)

def is_valid_position(x, y):
    return 0 <= x < 3 and 0 <= y < 3

def get_possible_moves(puzzle, blank_pos):
    x, y = blank_pos
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    
    for dx, dy in directions:
        if is_valid_position(x + dx, y + dy):
            new_puzzle = [row[:] for row in puzzle]
            new_pos = (x + dx, y + dy)
            tile_value = new_puzzle[new_pos[0]][new_pos[1]]
            new_puzzle[x][y], new_puzzle[new_pos[0]][new_pos[1]] = new_puzzle[new_pos[0]][new_pos[1]], 0
            moves.append((new_puzzle, tile_value))
    
    return moves

def manhattan_distance(puzzle, goal):
    distance = 0
    for i in range(3):
        for j in range(3):
            if puzzle[i][j] != 0:
                target_x, target_y = divmod(goal[i][j], 3)
                distance += abs(target_x - i) + abs(target_y - j)
    return distance

#  A* with trace logging
def a_star(start, goal):
    start_state = (manhattan_distance(start, goal), 0, start, find_blank(start))
    priority_queue = [start_state]
    heapq.heapify(priority_queue)
    closed_set = set()
    steps = 0
    trace = []

    while priority_queue:
        _, cost, current, blank_pos = heapq.heappop(priority_queue)

        # Log current state of fringe and closed set
        fringe_state = [state[2] for state in priority_queue]
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Fringe: {fringe_state}")
        trace.append(f"Closed set size: {len(closed_set)}")
        trace.append(f"Expanded nodes: {steps}")

        if current == goal:
            return {'solution': cost, 'nodes_expanded': steps, 'trace': trace}

        steps += 1
        closed_set.add(tuple(map(tuple, current)))

        for new_state, move_cost in get_possible_moves(current, blank_pos):
            if tuple(map(tuple, new_state)) not in closed_set:
                new_cost = cost + move_cost
                priority = new_cost + manhattan_distance(new_state, goal)
                heapq.heappush(priority_queue, (priority, new_cost, new_state, find_blank(new_state)))

    return {'solution': None, 'nodes_expanded': steps, 'trace': trace}

def dump_trace(trace):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    with open(f"trace-{current_time}.txt", 'w') as file:
        for line in trace:
            file.write(line + "\n")

# BFS with trace logging
def bfs(start, goal):
    frontier = deque([start])
    explored = set()
    steps = 0
    trace = []

    while frontier:
        current = frontier.popleft()
        blank_pos = find_blank(current)

        # Log current state of frontier and explored set
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Fringe: {list(frontier)}")
        trace.append(f"Closed set size: {len(explored)}")
        trace.append(f"Expanded nodes: {steps}")

        if current == goal:
            return {'solution': steps, 'nodes_expanded': steps, 'trace': trace}

        steps += 1
        explored.add(tuple(map(tuple, current)))

        for new_state, _ in get_possible_moves(current, blank_pos):
            if tuple(map(tuple, new_state)) not in explored and new_state not in frontier:
                frontier.append(new_state)

    return {'solution': None, 'nodes_expanded': steps, 'trace': trace}

# UCS with trace logging
def ucs(start, goal):
    frontier = [(0, start)]
    explored = set()
    steps = 0
    trace = []

    while frontier:
        cost, current = heapq.heappop(frontier)
        blank_pos = find_blank(current)

        # Log current state of frontier and explored set
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Fringe: {[item[1] for item in frontier]}")
        trace.append(f"Closed set size: {len(explored)}")
        trace.append(f"Expanded nodes: {steps}")

        if current == goal:
            return {'solution': cost, 'nodes_expanded': steps, 'trace': trace}

        steps += 1
        explored.add(tuple(map(tuple, current)))

        for new_state, move_cost in get_possible_moves(current, blank_pos):
            if tuple(map(tuple, new_state)) not in explored:
                new_cost = cost + move_cost
                heapq.heappush(frontier, (new_cost, new_state))

    return {'solution': None, 'nodes_expanded': steps, 'trace': trace}

# DFS with trace logging
def dfs(start, goal):
    frontier = [start]
    explored = set()
    steps = 0
    trace = []

    while frontier:
        current = frontier.pop()  # DFS uses a stack (LIFO)
        blank_pos = find_blank(current)

        # Log current state of frontier and explored set
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Fringe: {list(frontier)}")
        trace.append(f"Closed set size: {len(explored)}")
        trace.append(f"Expanded nodes: {steps}")

        if current == goal:
            return {'solution': steps, 'nodes_expanded': steps, 'trace': trace}

        steps += 1
        explored.add(tuple(map(tuple, current)))

        for new_state, _ in get_possible_moves(current, blank_pos):
            if tuple(map(tuple, new_state)) not in explored:
                frontier.append(new_state)

    return {'solution': None, 'nodes_expanded': steps, 'trace': trace}


# Greedy Search with trace logging
def greedy(start, goal):
    frontier = [(manhattan_distance(start, goal), start)]
    heapq.heapify(frontier)
    explored = set()
    steps = 0
    trace = []

    while frontier:
        _, current = heapq.heappop(frontier)
        blank_pos = find_blank(current)

        # Log current state of frontier and explored set
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Fringe: {[item[1] for item in frontier]}")
        trace.append(f"Closed set size: {len(explored)}")
        trace.append(f"Expanded nodes: {steps}")

        if current == goal:
            return {'solution': steps, 'nodes_expanded': steps, 'trace': trace}

        steps += 1
        explored.add(tuple(map(tuple, current)))

        for new_state, _ in get_possible_moves(current, blank_pos):
            if tuple(map(tuple, new_state)) not in explored:
                priority = manhattan_distance(new_state, goal)
                heapq.heappush(frontier, (priority, new_state))

    return {'solution': None, 'nodes_expanded': steps, 'trace': trace}

# DLS (Depth-Limited Search) with trace logging
def dls(start, goal, depth_limit):
    trace = []
    
    def recursive_dls(current, goal, depth, steps):
        trace.append(f"Step: {steps}")
        trace.append(f"Current node: {current}")
        trace.append(f"Remaining depth: {depth}")
        trace.append(f"Expanded nodes: {steps}")
        
        if current == goal:
            return {'solution': steps, 'nodes_expanded': steps, 'trace': trace}
        if depth == 0:
            return None
        
        blank_pos = find_blank(current)
        for new_state, _ in get_possible_moves(current, blank_pos):
            result = recursive_dls(new_state, goal, depth - 1, steps + 1)
            if result:
                return result

    return recursive_dls(start, goal, depth_limit, 0)

# IDS (Iterative Deepening Search) with trace logging
def ids(start, goal):
    depth = 0
    result = None
    trace = []

    while result is None:
        result = dls(start, goal, depth)
        depth += 1
        trace.append(f"IDS Depth Level: {depth}")

    return result

# Main function
def main():
    if len(sys.argv) < 3:
        print("Usage: python expense_8_puzzle.py <start-file> <goal-file> <method> <dump-flag>")
        return
    
    start_file = sys.argv[1]
    goal_file = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else "a*"
    dump_flag = sys.argv[4] if len(sys.argv) > 4 else "false"
    
    start_puzzle = read_puzzle(start_file)
    goal_puzzle = read_puzzle(goal_file)
    
    if method == "bfs":
        result = bfs(start_puzzle, goal_puzzle)
    elif method == "ucs":
        result = ucs(start_puzzle, goal_puzzle)
    elif method == "dfs":
        result = dfs(start_puzzle, goal_puzzle)
    elif method == "dls":
        depth_limit = int(input("Enter depth limit: "))
        result = dls(start_puzzle, goal_puzzle, depth_limit)
    elif method == "ids":
        result = ids(start_puzzle, goal_puzzle)
    elif method == "greedy":
        result = greedy(start_puzzle, goal_puzzle)
    else:
        result = a_star(start_puzzle, goal_puzzle)

    if dump_flag == "true":
        dump_trace(result['trace'])

    print("Solution cost:", result['solution'])
    print("Nodes expanded:", result['nodes_expanded'])

if __name__ == "__main__":
    main()
