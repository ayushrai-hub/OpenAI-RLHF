import unittest
import numpy as np

from ideal_completion import (
    produce_vocab,
    construct_sentence_iddfs,
    construct_sentence_ucs,
    construct_sentence_greedy,
    construct_sentence_astar,
)

class TestSentenceConstruction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        np.random.seed(42)

        cls.L = 3
        cls.n = 2
        cls.vocab = produce_vocab(cls.L)
        # Define a fixed transition matrix for testing
        cls.transition_matrix = np.array([
            [0.1, 0.6, 0.3],  # Transitions from t1 to t1, t2, t3
            [0.4, 0.4, 0.2],  # Transitions from t2
            [0.3, 0.3, 0.4],  # Transitions from t3
            [0.5, 0.3, 0.2],  # Transitions from <Start> to t1, t2, t3
            [0.2, 0.5, 0.3],  # Transitions from t1, t2, t3 to <End>
        ])
        cls.transition_matrix = cls.transition_matrix / cls.transition_matrix.sum(axis=1, keepdims=True)

    def test_construct_sentence_iddfs(self):
        # Test IDDFS constructs valid sentences and scores
        depth_limit = self.n
        result, nodes_traversed = construct_sentence_iddfs(self.vocab, self.transition_matrix, depth_limit)
        sentence, score = result
        self.assertIsInstance(sentence, list)
        self.assertIsInstance(score, float)
        self.assertIsInstance(nodes_traversed, int)
        self.assertGreaterEqual(len(sentence), 2) 
        self.assertGreater(nodes_traversed, 0)

    def test_construct_sentence_ucs(self):
        # Test UCS constructs valid sentences and scores
        n = self.n
        sentence, score, nodes_traversed = construct_sentence_ucs(self.vocab, self.transition_matrix, n)
        self.assertIsInstance(sentence, list)
        self.assertIsInstance(score, float)
        self.assertIsInstance(nodes_traversed, int)
        expected_length = n + 2  
        self.assertEqual(len(sentence), expected_length)
        self.assertGreater(nodes_traversed, 0)

    def test_construct_sentence_greedy(self):
        # Test greedy algorithm constructs valid sentences and scores
        n = self.n
        sentence, score, nodes_encountered = construct_sentence_greedy(self.vocab, self.transition_matrix, n)
        self.assertIsInstance(sentence, list)
        self.assertIsInstance(score, float)
        self.assertIsInstance(nodes_encountered, int)
        expected_length = n + 2 
        self.assertEqual(len(sentence), expected_length)
        self.assertGreater(nodes_encountered, 0)

    def test_construct_sentence_astar(self):
        # Test A* constructs valid sentences and scores
        n = self.n
        sentence, score, nodes_tally = construct_sentence_astar(self.vocab, self.transition_matrix, n)
        self.assertIsInstance(sentence, list)
        self.assertIsInstance(score, float)
        self.assertIsInstance(nodes_tally, int)
        expected_length = n + 2 
        self.assertEqual(len(sentence), expected_length)
        self.assertGreater(nodes_tally, 0)

    def test_empty_vocab(self):
        # Test handling of empty vocabulary
        vocab = []
        transition_matrix = np.array([[]]) 
        depth_limit = 2
        n = 2

        with self.assertRaises(IndexError):
            construct_sentence_iddfs(vocab, transition_matrix, depth_limit)
        with self.assertRaises(IndexError):
            construct_sentence_ucs(vocab, transition_matrix, n)
        with self.assertRaises(IndexError):
            construct_sentence_greedy(vocab, transition_matrix, n)
        with self.assertRaises(IndexError):
            construct_sentence_astar(vocab, transition_matrix, n)

    def test_all_zero_probabilities(self):
        # Test handling of all-zero transition probabilities
        vocab = produce_vocab(3)
        transition_matrix = np.zeros((5, 4)) 
        depth_limit = 2
        n = 2

        result, nodes = construct_sentence_iddfs(vocab, transition_matrix, depth_limit)
        self.assertEqual(result, ([], 0.0))
        self.assertGreaterEqual(nodes, 0)

        sentence, score, nodes = construct_sentence_ucs(vocab, transition_matrix, n)
        self.assertEqual(sentence, [])
        self.assertEqual(score, 0.0)

        sentence, score, nodes = construct_sentence_greedy(vocab, transition_matrix, n)
        self.assertEqual(sentence, ['<Start>', '<End>'])
        self.assertEqual(score, 0.0)

        sentence, score, nodes = construct_sentence_astar(vocab, transition_matrix, n)
        self.assertEqual(sentence, [])
        self.assertEqual(score, 0.0)

    def test_invalid_transition_matrix(self):
        # Test handling of invalid transition matrix dimensions
        vocab = produce_vocab(3)
        transition_matrix = np.array([
            [0.1, 0.9],  
            [0.4, 0.6],
        ])
        depth_limit = 2
        n = 2

        try:
            construct_sentence_iddfs(vocab, transition_matrix, depth_limit)
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))

        try:
            construct_sentence_ucs(vocab, transition_matrix, n)
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))

        try:
            construct_sentence_greedy(vocab, transition_matrix, n)
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))

        try:
            construct_sentence_astar(vocab, transition_matrix, n)
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))

    def test_single_word_vocab(self):
        # Test handling of single-word vocabulary
        vocab = ['t1']
        transition_matrix = np.array([
            [0.0],  
            [1.0],  
            [1.0],  
        ])
        depth_limit = 1
        n = 1

        result, nodes = construct_sentence_iddfs(vocab, transition_matrix, depth_limit)
        self.assertEqual(result[0], [])
        self.assertAlmostEqual(result[1], 0.0)

        sentence, score, nodes = construct_sentence_ucs(vocab, transition_matrix, n)
        self.assertEqual(sentence, [])
        self.assertAlmostEqual(score, 0.0)

        sentence, score, nodes = construct_sentence_greedy(vocab, transition_matrix, n)
        self.assertEqual(sentence, ['<Start>', '<End>'])
        self.assertAlmostEqual(score, 1.0)

        sentence, score, nodes = construct_sentence_astar(vocab, transition_matrix, n)
        self.assertEqual(sentence, [])
        self.assertAlmostEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)