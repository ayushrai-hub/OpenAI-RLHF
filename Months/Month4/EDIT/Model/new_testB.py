import unittest
from ideal_completion import EnvAgent, execute_with_relaxed_planning, relaxed_planning, Directions

class MockGridTransitionMap:
    def get_transitions(self, x, y, direction):
        return [True, True, True, True]  # Allows movement in all directions

class TestRelaxedPlanning(unittest.TestCase):
    def setUp(self):
        self.rail = MockGridTransitionMap()
        self.max_timestep = 100

    def test_single_agent_planning(self):
        # It tests planning with a single agent.
        agents = [EnvAgent((0, 0), Directions.EAST, (2, 2))]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        self.assertEqual(len(paths), 1)
        self.assertGreater(len(paths[0]), 0)
        self.assertEqual(paths[0][-1], (2, 2))  # Verify target reached

    def test_multiple_agents_full_planning(self):
        # It tests planning with multiple agents with full initial planning.
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),
            EnvAgent((2, 0), Directions.WEST, (0, 2))
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        self.assertEqual(len(paths), 2)
        for i, path in enumerate(paths):
            self.assertGreater(len(path), 0)
            self.assertEqual(path[-1], agents[i].target)

    def test_partial_planning(self):
        # It tests planning with partial initial planning.
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),
            EnvAgent((2, 0), Directions.WEST, (0, 2)),
            EnvAgent((1, 0), Directions.NORTH, (1, 2))
        ]
        initial_fraction = 0.33  # Only plan for first agent initially
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, initial_fraction)
        
        self.assertEqual(len(paths), 3)
        for i, path in enumerate(paths):
            self.assertGreater(len(path), 0)
            self.assertEqual(path[-1], agents[i].target)

    def test_edge_case_zero_agents(self):
        # It tests planning with zero agents
        agents = []
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        self.assertEqual(len(paths), 0)

    def test_edge_case_zero_fraction(self):
        # It tests planning with zero initial planning fraction.
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),
            EnvAgent((2, 0), Directions.WEST, (0, 2))
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 0.0)
        
        self.assertEqual(len(paths), 2)
        for i, path in enumerate(paths):
            self.assertGreater(len(path), 0)
            self.assertEqual(path[-1], agents[i].target)

    def test_path_validity(self):
        # It tests that paths are valid (continuous and within grid).
        agents = [EnvAgent((0, 0), Directions.EAST, (2, 2))]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        path = paths[0]
        for i in range(1, len(path)):
            # Check continuity (manhattan distance should be 1 between consecutive positions)
            prev_pos = path[i-1]
            curr_pos = path[i]
            manhattan_dist = abs(prev_pos[0] - curr_pos[0]) + abs(prev_pos[1] - curr_pos[1])
            self.assertEqual(manhattan_dist, 1)

    def test_collision_avoidance(self):
        # It tests that paths are collision-free.
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),
            EnvAgent((2, 0), Directions.WEST, (0, 2))
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        # Check for vertex conflicts
        max_path_length = max(len(path) for path in paths)
        for t in range(max_path_length):
            positions_at_t = set()
            for path in paths:
                if t < len(path):
                    pos = path[t]
                    self.assertNotIn(pos, positions_at_t)  # No two agents at same position
                    positions_at_t.add(pos)

        # Check for edge conflicts
        for t in range(1, max_path_length):
            for i, path1 in enumerate(paths):
                for j, path2 in enumerate(paths):
                    if i < j and t < len(path1) and t < len(path2):
                        # Check if agents swap positions
                        self.assertFalse(
                            path1[t-1] == path2[t] and path1[t] == path2[t-1]
                        )

    def test_max_timestep_constraint(self):
        # It testsTest that paths respect max_timestep constraint.
        small_max_timestep = 5
        agents = [EnvAgent((0, 0), Directions.EAST, (2, 2))]
        paths = execute_with_relaxed_planning(agents, self.rail, small_max_timestep, 1.0)
        
        for path in paths:
            self.assertLessEqual(len(path), small_max_timestep + 1)  # +1 for initial position

    def test_different_initial_directions(self):
        # It tests planning with different initial directions.
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),
            EnvAgent((2, 0), Directions.NORTH, (0, 2)),
            EnvAgent((1, 0), Directions.SOUTH, (1, 2))
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        self.assertEqual(len(paths), 3)
        for i, path in enumerate(paths):
            self.assertGreater(len(path), 0)
            self.assertEqual(path[-1], agents[i].target)

    def test_same_target_different_agents(self):
        # It tests planning with multiple agents targeting the same position.
        target = (2, 2)
        agents = [
            EnvAgent((0, 0), Directions.EAST, target),
            EnvAgent((2, 0), Directions.WEST, target)
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        # It verifies all agents eventually reach the target
        for path in paths:
            self.assertEqual(path[-1], target)
            
        # It verifies no collisions at target
        arrival_times = [len(path) - 1 for path in paths]
        self.assertEqual(len(set(arrival_times)), len(arrival_times))

    def test_unreachable_targets(self):
        # It tests agents with unreachable targets by creating a custom grid
        class RestrictedGridMap(MockGridTransitionMap):
            def get_transitions(self, x, y, direction):
                if y == 1:  # Create a blocked cell
                    return [False, False, False, False]
                return [True, True, True, True]
                
        restricted_rail = RestrictedGridMap()
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 2)),  # Must pass through (1,1)
        ]
        paths = execute_with_relaxed_planning(agents, restricted_rail, self.max_timestep, 1.0)
        self.assertTrue(
        len(paths[0]) == 0 or paths[0][-1] != agents[0].target)

    def test_complex_path_planning(self):
        # It tests paths requiring multiple direction changes and potential backtracking
        agents = [
            EnvAgent((0, 0), Directions.EAST, (0, 2)),  # Requires U-turn
            EnvAgent((1, 0), Directions.NORTH, (1, 3))  # Requires zigzag
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        # It verifies paths contain necessary direction changes
        path1 = paths[0]
        self.assertGreater(len(path1), 2)  # Path should be longer than direct route
        
        # It checks for direction changes in the path
        directions_changed = True
        for i in range(1, len(path1)-1):
            prev_dir = (path1[i][0] - path1[i-1][0], path1[i][1] - path1[i-1][1])
            next_dir = (path1[i+1][0] - path1[i][0], path1[i+1][1] - path1[i][1])
            if prev_dir != next_dir:
                directions_changed = False
        self.assertTrue(directions_changed)

    def test_tight_timestep_constraints(self):
        # It tests with very tight timestep constraints
        agents = [
            EnvAgent((0, 0), Directions.EAST, (3, 3)),  # Requires at least 6 steps
        ]
        # It tests with insufficient timesteps
        paths = execute_with_relaxed_planning(agents, self.rail, max_timestep=4, initial_planning_fraction=1.0 )
        self.assertEqual(len(paths[0]), 0)  # Should return empty path

    def test_multiple_collision_scenarios(self):
        # It tests various collision scenarios
        agents = [
            # Head-on collision scenario
            EnvAgent((0, 0), Directions.EAST, (2, 0)),
            EnvAgent((2, 0), Directions.WEST, (0, 0)),
            # Cross-path collision scenario
            EnvAgent((1, 0), Directions.NORTH, (1, 2)),
            EnvAgent((0, 1), Directions.EAST, (2, 1))
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        # It checks for all types of collisions
        max_length = max(len(p) for p in paths)
        for t in range(max_length):
            # It checks vertex collisions
            positions = set()
            for path in paths:
                if t < len(path):
                    self.assertNotIn(path[t], positions)
                    positions.add(path[t])
                    
            # It checks edge collisions
            if t > 0:
                for i in range(len(paths)):
                    for j in range(i+1, len(paths)):
                        if t < len(paths[i]) and t < len(paths[j]):
                            self.assertFalse(
                                paths[i][t-1] == paths[j][t] and 
                                paths[i][t] == paths[j][t-1]
                            )

    def test_fraction_rounding_behavior(self):
        # It tests fraction rounding behavior with odd numbers of agents
        agents = [
            EnvAgent((0, i), Directions.EAST, (2, i)) 
            for i in range(5)  # 5 agents
        ]
        
        # It tests with fraction that should round to 2 agents
        paths_compendium, pending_agents = relaxed_planning(
            agents, self.rail, self.max_timestep, 0.45
        )
        self.assertEqual(sum(1 for p in paths_compendium if p), 2)
        
        # It tests with very small fraction
        paths_compendium, pending_agents = relaxed_planning(
            agents, self.rail, self.max_timestep, 0.01
        )
        self.assertEqual(sum(1 for p in paths_compendium if p), 0)

    def test_grid_boundaries(self):
        # It tests agents near grid edges
        agents = [
            EnvAgent((0, 0), Directions.WEST, (0, 2)),  # Starting at left edge
            EnvAgent((10, 0), Directions.EAST, (10, 2)),  # Starting at right edge
        ]
        paths = execute_with_relaxed_planning(agents, self.rail, self.max_timestep, 1.0)
        
        # It checks paths are found despite edge positions
        for i, path in enumerate(paths):
            self.assertGreater(len(path), 0)
            self.assertEqual(path[-1], agents[i].target)

if __name__ == '__main__':
    unittest.main(verbosity=2)