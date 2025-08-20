import unittest
from unittest.mock import patch, mock_open
from testableIC import bfs, a_star, dfs, ucs, greedy, dls, ids, dump_trace, main

class TestExpense8Puzzle(unittest.TestCase):
    # Sample start and goal puzzles for testing
    start_puzzle = [
        [1, 2, 3],
        [4, 0, 5],
        [7, 8, 6]
    ]

    goal_puzzle = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]

    # Mock the read_puzzle function to simulate file input
    @patch('ideal_completion.read_puzzle')
    def test_bfs(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = bfs(self.start_puzzle, self.goal_puzzle)
        self.assertEqual(result['solution'], 12)
        self.assertEqual(result['nodes_expanded'], 12)

    @patch('ideal_completion.read_puzzle')
    def test_a_star(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = a_star(self.start_puzzle, self.goal_puzzle)
        self.assertEqual(result['solution'], 11)  # Assume A* finds an optimal solution with cost 11
        self.assertEqual(result['nodes_expanded'], 13)

    @patch('ideal_completion.read_puzzle')
    def test_dfs(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = dfs(self.start_puzzle, self.goal_puzzle)
        self.assertEqual(result['solution'], 2)
        self.assertEqual(result['nodes_expanded'], 2)

    @patch('ideal_completion.read_puzzle')
    def test_ucs(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = ucs(self.start_puzzle, self.goal_puzzle)
        self.assertEqual(result['solution'], 11)  # UCS should find the optimal cost
        self.assertEqual(result['nodes_expanded'], 17)

    @patch('ideal_completion.read_puzzle')
    def test_greedy(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = greedy(self.start_puzzle, self.goal_puzzle)
        self.assertEqual(result['solution'], 2)
        self.assertEqual(result['nodes_expanded'], 2)

    @patch('ideal_completion.read_puzzle')
    def test_dls(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = dls(self.start_puzzle, self.goal_puzzle, 15)  # Test with a depth limit of 15
        self.assertIsNotNone(result)  # Ensure that DLS returns a result
        self.assertEqual(result['solution'], 14)

    @patch('ideal_completion.read_puzzle')
    def test_ids(self, mock_read_puzzle):
        mock_read_puzzle.side_effect = [self.start_puzzle, self.goal_puzzle]
        result = ids(self.start_puzzle, self.goal_puzzle)
        self.assertIsNotNone(result)  # Ensure that IDS returns a result
        self.assertEqual(result['solution'], 2)

    # Test trace dumping by capturing file output
    @patch('builtins.open', new_callable=mock_open)
    def test_dump_trace(self, mock_file):
        trace = ["Fringe: []", "Closed set size: 5", "Expanded nodes: 10"]
        dump_trace(trace)
        mock_file.assert_called_once()
        mock_file().write.assert_any_call("Fringe: []\n")
        mock_file().write.assert_any_call("Closed set size: 5\n")
        mock_file().write.assert_any_call("Expanded nodes: 10\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)
