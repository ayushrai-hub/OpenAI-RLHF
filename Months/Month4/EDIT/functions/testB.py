import unittest
import numpy as np
from ideal_completion import QAgent, sample_bid_with_valuation, strategy_fp

class TestIdealCompletion(unittest.TestCase):

    def test_sample_bid_with_valuation(self):
        # Mock percentiles data
        percentiles = {
            0: {
                "5th": np.linspace(0.1, 0.2, 10),
                "median": np.linspace(0.15, 0.25, 10),
                "95th": np.linspace(0.2, 0.3, 10),
            }
        }
        valuation = 0.5
        agent_index = 0

        # Since granularity is 10, valuation_index should be 4 (int(0.5*(10-1))=4.5->4)
        valuation_index = int(valuation * (len(percentiles[agent_index]["median"]) - 1))
        expected_low = percentiles[agent_index]["5th"][valuation_index]
        expected_high = percentiles[agent_index]["95th"][valuation_index]

        # Fix the random seed
        np.random.seed(42)
        sampled_bid = sample_bid_with_valuation(percentiles, valuation, agent_index)

        self.assertTrue(expected_low <= sampled_bid <= expected_high,
                        "Sampled bid should be between the 5th and 95th percentiles.")

        # Compute expected sampled bid for given low and high with fixed seed
        np.random.seed(42)
        expected_sampled_bid = np.random.uniform(expected_low, expected_high)
        self.assertEqual(sampled_bid, expected_sampled_bid, "Sampled bid should match expected value with fixed seed.")

    def test_qagent_select_action(self):
        # Create a QAgent with predefined Q-values
        actions = np.array([0, 1, 2])
        agent = QAgent(value_distr=lambda: 0.5, act_min=0, act_max=2, granularity=1)
        agent.actions = actions
        agent.q_values = np.array([[10, 20, 30]])  # One state, three actions

        # Test with epsilon = 0 (pure exploitation)
        agent.epsilon = 0
        selected_action = agent.select_action()
        self.assertEqual(selected_action, 2, "Agent should select the action with the highest Q-value.")

        # Test with epsilon = 1 (pure exploration)
        agent.epsilon = 1
        np.random.seed(42)
        selected_action = agent.select_action()
        self.assertIn(selected_action, actions, "Agent should select a random action.")
        # With seed 42 and actions [0,1,2], np.random.choice should select action 0
        self.assertEqual(selected_action, 0, "Agent should randomly select action 0 with seed 42.")

    def test_strategy_fp(self):
        bids = [0.5, 0.7, 0.7, 0.6]
        np.random.seed(42)
        winner, payment = strategy_fp(bids)
        self.assertEqual(winner, 1, "With seed 42, winner should be bidder at index 1.")
        self.assertEqual(payment, 0.7, "Payment should be equal to the highest bid.")

    def test_invalid_inputs(self):
        # Test negative valuations
        with self.assertRaises(ValueError):
            sample_bid_with_valuation({0: {"5th": [0.1], "median": [0.15], "95th": [0.2]}}, -0.5, 0)
        
        # Test valuations > 1
        with self.assertRaises(ValueError):
            sample_bid_with_valuation({0: {"5th": [0.1], "median": [0.15], "95th": [0.2]}}, 1.5, 0)
            
        # Test invalid agent index
        with self.assertRaises(KeyError):
            sample_bid_with_valuation({0: {"5th": [0.1], "median": [0.15], "95th": [0.2]}}, 0.5, 1)
            
        # Test malformed percentiles dict
        with self.assertRaises(KeyError):
            sample_bid_with_valuation({0: {"5th": [0.1], "95th": [0.2]}}, 0.5, 0)
            
        # Test None values
        with self.assertRaises(TypeError):
            sample_bid_with_valuation(None, 0.5, 0)

    def test_boundary_valuations(self):
        percentiles = {
            0: {
                "5th": np.linspace(0, 0.1, 10),
                "median": np.linspace(0.05, 0.15, 10), 
                "95th": np.linspace(0.1, 0.2, 10)
            }
        }
        
        # Test valuation = 0
        bid = sample_bid_with_valuation(percentiles, 0, 0)
        self.assertTrue(0 <= bid <= percentiles[0]["95th"][0])
        
        # Test valuation = 1
        bid = sample_bid_with_valuation(percentiles, 1, 0) 
        self.assertTrue(percentiles[0]["5th"][-1] <= bid <= percentiles[0]["95th"][-1])
        
        # Test very small valuation
        bid = sample_bid_with_valuation(percentiles, 1e-6, 0)
        self.assertTrue(percentiles[0]["5th"][0] <= bid <= percentiles[0]["95th"][0])

    def test_special_cases(self):
        # Test empty bid array
        with self.assertRaises(ValueError):
            strategy_fp([])
            
        # Test single bid
        winner, payment = strategy_fp([0.5])
        self.assertEqual(winner, 0)
        self.assertEqual(payment, 0.5)
        
        # Test all identical bids
        np.random.seed(42)
        winner, payment = strategy_fp([0.5, 0.5, 0.5])
        self.assertEqual(payment, 0.5)
        self.assertTrue(0 <= winner < 3)
        
        # Test max possible bids
        winner, payment = strategy_fp([1.0, 0.8, 0.9])
        self.assertEqual(winner, 0)
        self.assertEqual(payment, 1.0)
        
        # Test min possible bids  
        winner, payment = strategy_fp([0.0, 0.0, 0.0])
        self.assertEqual(payment, 0.0)

    def test_qagent_edge_cases(self):
        agent = QAgent(value_distr=lambda: 0.5, act_min=0, act_max=1, granularity=3)
        
        # Test state transitions
        agent.valuation = 0
        self.assertEqual(agent._get_state(0), 0)
        agent.valuation = 1
        self.assertEqual(agent._get_state(1), 2)
        
        # Test Q-value updates
        initial_q = agent.q_values[0,0]
        agent.update_q(agent.actions[0], 1.0)
        self.assertEqual(agent.q_values[0,0], initial_q)
        
        # Test multiple states
        agent = QAgent(value_distr=lambda: 0.5, act_min=0, act_max=1, granularity=5)
        self.assertEqual(agent.q_values.shape, (5, 5))
        
        # Test epsilon decay over time
        agent.epsilon = 0.9
        for i in range(1000):
            agent.epsilon_reduction(i)
        self.assertLess(agent.epsilon, 0.9)

    def test_performance_limits(self):
        # Test with large bid arrays
        large_bids = np.random.rand(10000)
        winner, payment = strategy_fp(large_bids)
        self.assertEqual(payment, np.max(large_bids))
        
        # Test with many agents
        many_agents = [QAgent(value_distr=lambda: 0.5) for _ in range(100)]
        self.assertEqual(len(many_agents), 100)
        
        # Basic computation time check
        import time
        start = time.time()
        strategy_fp(np.random.rand(1000))
        duration = time.time() - start
        self.assertLess(duration, 1.0)  # Should complete in under 1 second

if __name__ == "__main__":
    unittest.main(verbosity=2)