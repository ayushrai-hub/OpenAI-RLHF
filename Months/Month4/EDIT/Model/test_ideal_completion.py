
import unittest
from ideal_completion import EnvAgent, execute_with_relaxed_planning, relaxed_planning

class Directions:
    NORTH, EAST, SOUTH, WEST = range(4)

class MockGridTransitionMap:
    def get_transitions(self, x, y, direction):
        # For simplicity, agents can move to any adjacent cell without restriction
        # Returns a list [NORTH, EAST, SOUTH, WEST], where True indicates a possible transition
        return [True, True, True, True]

class TestRelaxedPlanning(unittest.TestCase):

    def setUp(self):
        self.rail = MockGridTransitionMap()
        self.max_timestep = 10
        self.initial_planning_fraction = 0.5

    def test_initial_agents_planned_correctly(self):
        agents = [
            EnvAgent((0, 0), Directions.EAST, (5, 5)),
            EnvAgent((1, 0), Directions.EAST, (5, 5)),
            EnvAgent((2, 0), Directions.EAST, (5, 5)),
            EnvAgent((3, 0), Directions.EAST, (5, 5))
        ]
        path_compendium, pending_agents = relaxed_planning(
            agents, self.rail, self.max_timestep, self.initial_planning_fraction
        )
        num_initially_planned_paths = sum(1 for path in path_compendium if path)
        self.assertEqual(num_initially_planned_paths, 2, "Initially, only half of the agents should be planned")
        self.assertEqual(len(pending_agents), 2, "There should be two agents pending planning")

    def test_all_agents_have_paths_after_execution(self):
        agents = [
            EnvAgent((0, 0), Directions.EAST, (5, 5)),
            EnvAgent((1, 0), Directions.EAST, (5, 5)),
            EnvAgent((2, 0), Directions.EAST, (5, 5)),
            EnvAgent((3, 0), Directions.EAST, (5, 5))
        ]
        path_compendium = execute_with_relaxed_planning(
            agents, self.rail, self.max_timestep, self.initial_planning_fraction
        )
        num_planned_paths = sum(1 for path in path_compendium if path)
        self.assertEqual(num_planned_paths, 4, "All agents should have paths after execution")
        for agent_id, path in enumerate(path_compendium):
            self.assertIsNotNone(path, f"Agent {agent_id} should have a path")
            self.assertTrue(len(path) > 0, f"Agent {agent_id}'s path should not be empty")

    def test_agents_reach_their_targets(self):
        agents = [
            EnvAgent((0, 0), Directions.EAST, (2, 0)),
            EnvAgent((1, 0), Directions.EAST, (3, 0))
        ]
        path_compendium = execute_with_relaxed_planning(
            agents, self.rail, self.max_timestep, initial_planning_fraction=1.0
        )
        for agent_id, agent in enumerate(agents):
            agent_path = path_compendium[agent_id]
            self.assertEqual(agent_path[-1], agent.target, f"Agent {agent_id} should reach its target")

if __name__ == '__main__':
    unittest.main(verbosity=2)
