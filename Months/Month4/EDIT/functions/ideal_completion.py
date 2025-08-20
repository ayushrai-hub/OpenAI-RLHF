# ideal_completion.py

import numpy as np

class QAgent:
    def __init__(self, value_distr, act_min=0, act_max=1, granularity=21, epsilon=0.1, alpha=0.1):
        self.value_distr = value_distr
        self.actions = np.linspace(act_min, act_max, granularity)
        self.epsilon = epsilon
        self.alpha = alpha
        self.granularity = granularity
        self.q_values = np.zeros((granularity, len(self.actions)))
        self.valuation = self.value_distr()
        self.state = self._get_state(self.valuation)
    
    def _get_state(self, valuation):
        if not 0 <= valuation <= 1:
            raise ValueError("Valuation must be between 0 and 1")
        bins = np.linspace(0, 1, self.granularity)
        state = np.argmin(np.abs(bins - valuation))
        return state
    
    def select_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        else:
            state_q_values = self.q_values[self.state]
            max_q = np.max(state_q_values)
            max_actions = np.where(state_q_values == max_q)[0]
            selected_index = np.random.choice(max_actions)
            return self.actions[selected_index]
            
    def update_q(self, action, reward):
        action_index = np.where(self.actions == action)[0][0]
        current_q = self.q_values[self.state, action_index]
        self.q_values[self.state, action_index] = current_q + self.alpha * (reward - current_q)
        
    def epsilon_reduction(self, current_round):
        if current_round < 0.66 * 1000:  # Using 1000 as default number of rounds
            self.epsilon = 0.99 - (0.94 * current_round / (0.66 * 1000))
        else:
            self.epsilon = 0.05

def sample_bid_with_valuation(percentiles, valuation, agent_index):
    if percentiles is None:
        raise TypeError("Percentiles cannot be None")
    if not 0 <= valuation <= 1:
        raise ValueError("Valuation must be between 0 and 1")
    if agent_index not in percentiles:
        raise KeyError(f"Agent index {agent_index} not found in percentiles")
    
    agent_percentiles = percentiles[agent_index]
    required_keys = ["5th", "median", "95th"]
    if not all(key in agent_percentiles for key in required_keys):
        raise KeyError("Percentiles dictionary must contain '5th', 'median', and '95th' keys")
        
    granularity = len(agent_percentiles['median'])
    valuation_index = int(valuation * (granularity - 1))
    low = agent_percentiles["5th"][valuation_index]
    high = agent_percentiles["95th"][valuation_index]
    return np.random.uniform(low, high)

def strategy_fp(bids):
    if len(bids) == 0:  # Fixed the array length check
        raise ValueError("Bids array cannot be empty")
    max_bid = np.max(bids)
    max_bidders = np.where(bids == max_bid)[0]
    winner = np.random.choice(max_bidders)
    payment = max_bid
    return winner, payment