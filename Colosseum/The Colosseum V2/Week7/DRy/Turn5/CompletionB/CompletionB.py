import numpy as np
import pandas as pd
from typing import List

# --- STUBS FOR DEMONSTRATION PURPOSES ---
# In your real code, you likely already have these classes defined
class BaseModel:
    pass

class UserSelection(BaseModel):
    """
    A sample class representing the user's selection.
    
    Required attributes:
      - prompt: the selected prompt (a string).
      - numDeepDive: number of recommendations for a “deep dive”.
      - numExploration: number of recommendations for exploration.
      - parameters: a dictionary with parameter values (used for parameterized recommendations).
    """
    def __init__(self, prompt: str, numDeepDive: int, numExploration: int, parameters: dict = None):
        self.prompt = prompt
        self.numDeepDive = numDeepDive
        self.numExploration = numExploration
        self.parameters = parameters if parameters is not None else {}

class PromptsManager:
    """
    Manages a DataFrame of prompts and a dictionary of cluster distances.
    """
    def __init__(self, df_prompts: pd.DataFrame, cluster_distances: dict):
        self.df_prompts = df_prompts
        self.cluster_distances = cluster_distances

class HistoryLogger(BaseModel):
    """
    A stub history manager for logging and storing probabilities.
    
    It holds:
      - prompts_manager: an instance of PromptsManager.
      - prompt_probabilities: a dictionary with two keys, 
           'no_params' for prompts without parameters and 
           'params' for prompts with parameters.
    """
    def __init__(self, prompts_manager: PromptsManager, org_id: str, id: str):
        self.prompts_manager = prompts_manager
        self.org_id = org_id
        self.id = id
        self.prompt_probabilities = {
            'no_params': {},
            'params': {}
        }
    
    def update_prompt_probabilities(self, recommended_prompts: List[str], params, mode: str):
        # In your implementation, this would update internal state or write a log.
        print(f"[HistoryLogger] Mode: {mode}, Prompts: {recommended_prompts}, Params: {params}")

# --- RECOMMENDER CLASSES ---
class MainRecommender(BaseModel):
    """
    Base class for recommendation algorithms.
    """
    def __init__(self, user_selection: UserSelection, history_manager: HistoryLogger):
        self.user_selection = user_selection
        self.history_manager = history_manager

    def detailed_recommendation(self):
        """
        DFS-type (deep dive) recommendation.
        Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def general_recommendation(self):
        """
        BFS-type (exploration) recommendation.
        Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        """
        Normalize a list of probabilities so that they sum to 1.
        """
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the group is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts: List[str], params, mode: str):
        """
        Update the history logger with the recommended prompts.
        """
        self.history_manager.update_prompt_probabilities(recommended_prompts, params=params, mode=mode)

class NoParamsRecommendation(MainRecommender):
    """
    Recommendation logic for prompts that do not have extra parameters.
    """
    def get_label_for_prompt(self, prompt: str) -> str:
        """
        Look up the label for a given prompt from the DataFrame.
        """
        df = self.history_manager.prompts_manager.df_prompts
        return df[df['prompts'] == prompt]['labels'].iloc[0]

    def filter_prompts_by_label(self, label: str) -> List[str]:
        """
        Return all prompts with the given label which also have an empty parameters list.
        """
        df = self.history_manager.prompts_manager.df_prompts
        mask = (df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))
        return df[mask]['prompts'].tolist()

    def compute_no_params_probs(self, prompts_list: List[str]) -> List[float]:
        """
        Get the probability for each prompt from the history manager.
        If a prompt is not yet in the dictionary, assume a default value of 1.
        """
        return [self.history_manager.prompt_probabilities['no_params'].get(p, 1) for p in prompts_list]

    def detailed_recommendation(self):
        """
        DFS recommendation: choose prompts having the same label (cluster) as the selected prompt,
        and with no parameters.
        """
        prompt = self.user_selection.prompt
        label = self.get_label_for_prompt(prompt)
        possible_prompts = self.filter_prompts_by_label(label)
        if not possible_prompts:
            print("No matching prompts found for DFS recommendation (no parameters).")
            return []
        probs = self.compute_no_params_probs(possible_prompts)
        standardized_probs = self.standardize_probabilities(probs)
        num = self.user_selection.numDeepDive
        recommended_prompts = list(np.random.choice(possible_prompts, size=num, replace=False, p=standardized_probs))
        self.update_history_manager(recommended_prompts, params=[None] * num, mode='recommendations')
        return recommended_prompts

    def general_recommendation(self):
        """
        BFS recommendation: select prompts from a close (but different) cluster.
        The “closest” cluster is determined from the cluster_distances dictionary.
        """
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = self.get_label_for_prompt(prompt)
        cluster_distances = self.history_manager.prompts_manager.cluster_distances
        
        # Find the closest cluster (other label)
        relevant = {pair: dist for pair, dist in cluster_distances.items() if label in pair}
        min_distance = float('inf')
        closest_label = None
        for pair, dist in relevant.items():
            parts = pair.split(',')
            other_label = parts[0] if parts[1] == label else parts[1]
            if dist < min_distance:
                min_distance = dist
                closest_label = other_label
        if not closest_label:
            print("No closest cluster found for BFS recommendation.")
            return []
        possible_prompts = self.filter_prompts_by_label(closest_label)
        if not possible_prompts:
            print("No matching prompts found for BFS recommendation (no parameters) in closest cluster.")
            return []
        probs = self.compute_no_params_probs(possible_prompts)
        standardized_probs = self.standardize_probabilities(probs)
        num = self.user_selection.numExploration
        recommended_prompts = list(np.random.choice(possible_prompts, size=num, replace=False, p=standardized_probs))
        self.update_history_manager(recommended_prompts, params=[None] * num, mode='recommendations')
        return recommended_prompts

class ParamRecommendation(MainRecommender):
    """
    Recommendation logic for prompts that include parameters.
    """
    def get_key_param_for_prompt(self, prompt: str):
        """
        For a parameterized prompt, assume the first item in the 'params' list is the key parameter.
        """
        df = self.history_manager.prompts_manager.df_prompts
        return df[df['prompts'] == prompt]['params'].iloc[0][0]

    def filter_prompts_by_key_param(self, key_param) -> List[str]:
        """
        Return all prompts that have parameters exactly equal to [key_param].
        (This can be customized to suit your needs.)
        """
        df = self.history_manager.prompts_manager.df_prompts
        mask = df['params'].apply(lambda x: x == [key_param])
        return df[mask]['prompts'].tolist()

    def compute_params_probs(self, prompts_list: List[str], key_param, key_param_value) -> List[float]:
        """
        For each prompt, get (and if necessary initialize) the probability associated with key_param_value.
        """
        probs = []
        for p in prompts_list:
            prompt_param_probs = self.history_manager.prompt_probabilities['params'].setdefault(p, {})
            key_param_probs = prompt_param_probs.setdefault(key_param, {})
            if key_param_value not in key_param_probs:
                key_param_probs[key_param_value] = 1
            probs.append(key_param_probs[key_param_value])
        return probs

    def detailed_recommendation(self):
        """
        DFS recommendation for parameterized prompts.
        """
        prompt = self.user_selection.prompt
        key_param = self.get_key_param_for_prompt(prompt)
        possible_prompts = self.filter_prompts_by_key_param(key_param)
        if not possible_prompts:
            print("No matching parameterized prompts found for DFS recommendation.")
            return []
        key_param_value = self.user_selection.parameters.get(key_param)
        if key_param_value is None:
            print(f"No parameter value provided for key parameter '{key_param}'.")
            return []
        probs = self.compute_params_probs(possible_prompts, key_param, key_param_value)
        standardized_probs = self.standardize_probabilities(probs)
        num = self.user_selection.numDeepDive
        recommended_prompts = list(np.random.choice(possible_prompts, size=num, replace=False, p=standardized_probs))
        self.update_history_manager(recommended_prompts, params=[{key_param: key_param_value}] * num, mode='recommendations')
        return recommended_prompts

    def general_recommendation(self):
        """
        BFS recommendation for parameterized prompts falls back to the no-parameter logic (using the same label).
        """
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        # Filter to only those prompts that have no parameters
        mask = (df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))
        possible_prompts = df[mask]['prompts'].tolist()
        if not possible_prompts:
            print("No matching no-parameter prompts found for BFS recommendation in parameterized context.")
            return []
        probs = [self.history_manager.prompt_probabilities['no_params'].get(p, 1) for p in possible_prompts]
        standardized_probs = self.standardize_probabilities(probs)
        num = self.user_selection.numExploration
        recommended_prompts = list(np.random.choice(possible_prompts, size=num, replace=False, p=standardized_probs))
        self.update_history_manager(recommended_prompts, params=[None] * num, mode='recommendations')
        return recommended_prompts

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Create a dummy DataFrame with columns 'prompts', 'labels', and 'params'
    data = {
        'prompts': ['prompt1', 'prompt2', 'prompt3', 'prompt4', 'prompt5', 'prompt6'],
        'labels': ['A', 'A', 'B', 'B', 'B', 'C'],
        'params': [[], [], ['paramX'], ['paramX'], [], []]  # prompt3 & prompt4 are parameterized
    }
    df_prompts = pd.DataFrame(data)
    
    # Dummy dictionary for cluster distances between labels (clusters)
    cluster_distances = {
        "A,B": 0.5,
        "A,C": 0.7,
        "B,C": 0.4
    }
    
    # Create a PromptsManager instance
    prompts_manager = PromptsManager(df_prompts, cluster_distances)
    
    # Set up some initial prompt probabilities
    prompt_probabilities = {
        'no_params': {'prompt1': 1, 'prompt2': 2, 'prompt5': 1, 'prompt6': 1},
        'params': {
            'prompt3': {'paramX': {'value1': 1}},
            'prompt4': {'paramX': {'value1': 2}}
        }
    }
    
    # Create a HistoryLogger instance and assign probabilities
    history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id="org123", id="id123")
    history_manager.prompt_probabilities = prompt_probabilities

    # --- No-parameters Recommendation Example ---
    user_selection_no_params = UserSelection(prompt="prompt1", numDeepDive=1, numExploration=1)
    no_param_rec = NoParamsRecommendation(user_selection=user_selection_no_params, history_manager=history_manager)
    print("NoParams DFS recommendations:", no_param_rec.detailed_recommendation())
    print("NoParams BFS recommendations:", no_param_rec.general_recommendation())
    
    # --- Parameterized Recommendation Example ---
    user_selection_params = UserSelection(prompt="prompt3", numDeepDive=1, numExploration=1, parameters={'paramX': 'value1'})
    param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)
    print("Param DFS recommendations:", param_rec.detailed_recommendation())
    print("Param BFS recommendations:", param_rec.general_recommendation())
