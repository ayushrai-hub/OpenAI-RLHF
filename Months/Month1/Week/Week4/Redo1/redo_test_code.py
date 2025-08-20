import unittest
import pandas as pd
import numpy as np
from itertools import product

# Import the functions to be tested
from redo_ideal import marginal_probability, joint_probability, check_conditional_independence

class TestJPDandDAG(unittest.TestCase):
    def setUp(self):
        # Sample data for testing
        self.sample_df = pd.DataFrame({
            'A': [True, True, False, False],
            'B': [True, False, True, False],
            'P': [0.3, 0.2, 0.1, 0.4]
        })

        # Full dataset from the original code
        self.full_df = pd.DataFrame({
            'A': [True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
            'B': [True, True, True, True, False, False, False, False, True, True, True, True, False, False, False, False],
            'C': [True, True, False, False, True, True, False, False, True, True, False, False, True, True, False, False],
            'D': [True, False, True, False, True, False, True, False, True, False, True, False, True, False, True, False],
            'P': [0.014, 0.042, 0.0126, 0.0714, 0.056, 0.168, 0.0504, 0.2856, 0.00375, 0.01125, 0.02025, 0.11475, 0.00375, 0.01125, 0.02025, 0.11475]
        })

    def test_joint_probability(self):
        # Test with no variables
        self.assertEqual(joint_probability(self.sample_df, []), {(): 1.0})
        
        # Test with one variable
        expected_A = {(True,): 0.5, (False,): 0.5}
        self.assertEqual(joint_probability(self.sample_df, ['A']), expected_A)
        
        # Test with two variables
        expected_AB = {(True, True): 0.3, (True, False): 0.2, (False, True): 0.1, (False, False): 0.4}
        self.assertEqual(joint_probability(self.sample_df, ['A', 'B']), expected_AB)

    def test_check_independence(self):
        # Test independence (A and B are not independent in this sample)
        self.assertFalse(check_conditional_independence(self.sample_df, 'A', 'B', []))
        
        # Test conditional independence (A and B are conditionally independent given themselves)
        self.assertTrue(check_conditional_independence(self.sample_df, 'A', 'B', ['A']))
        self.assertTrue(check_conditional_independence(self.sample_df, 'A', 'B', ['B']))

    def test_dag_a_conditional_independencies(self):
        self.assertTrue(check_conditional_independence(self.full_df, 'B', 'C', ['A']))
        self.assertTrue(check_conditional_independence(self.full_df, 'B', 'D', ['A', 'C']))

    def test_dag_b_conditional_independencies(self):
        self.assertFalse(check_conditional_independence(self.full_df, 'A', 'C', ['B', 'D']))
        self.assertFalse(check_conditional_independence(self.full_df, 'B', 'D', []))
        self.assertFalse(check_conditional_independence(self.full_df, 'B', 'C', []))

    def test_match_dag(self):
        # DAG (a)
        match_DAG_a = all([
            check_conditional_independence(self.full_df, 'B', 'C', ['A']),
            check_conditional_independence(self.full_df, 'B', 'D', ['A', 'C'])
        ])
        self.assertTrue(match_DAG_a)

        # DAG (b)
        match_DAG_b = all([
            check_conditional_independence(self.full_df, 'A', 'C', ['B', 'D']),
            check_conditional_independence(self.full_df, 'B', 'D', []),
            check_conditional_independence(self.full_df, 'B', 'C', [])
        ])
        self.assertFalse(match_DAG_b)

if __name__ == '__main__':
    unittest.main(verbosity=2)