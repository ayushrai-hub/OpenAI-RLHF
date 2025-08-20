from typing import List
import numpy as np

class BaseModel:
    # Placeholder for whatever BaseModel is in your code
    pass

class UserChoice:
    # Placeholder for structure, make sure it has attributes prompt, parameters, etc.
    def __init__(self, prompt: str, parameters: dict, numDeepDive: int, numExploration: int):
        self.prompt = prompt
        self.parameters = parameters
        self.numDeepDive = numDeepDive
        self.numExploration = numExploration

class HistoryManager:
    # Placeholder based on original code
    def __init__(self, prompts_mgr, org_id, id):
        self.prompts_mgr = prompts_mgr
        self.org_id = org_id
        self.id = id
        self.prompt_probs = {
            "no_params": {},
            "params": {}
        }

    def update_prompt_probs(self, recommended_prompts: List[str], params: List[dict], mode: str):
        # Implementation for updating prompt probabilities/history
        pass

class PromptsManager:
    # Placeholder based on original code
    def __init__(self, df_prompts, cluster_distances):
        self.df_prompts = df_prompts
        self.cluster_distances = cluster_distances

class BaseRecommender(BaseModel):
    def __init__(self, user_choice: UserChoice, history_mgr: HistoryManager):
        self.user_choice = user_choice
        self.history_mgr = history_mgr

    def deep_dive_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def exploration_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        if not probs or sum(probs) == 0:
            print("Total probability is zero or no probabilities provided.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts: List[str], params: List[dict], mode: str):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def get_label_from_prompt(self, prompt: str) -> str:
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        return label

class NoParamsRecommender(BaseRecommender):

    def find_candidate_prompts_no_params(self, label: str) -> List[str]:
        df = self.history_mgr.prompts_mgr.df_prompts
        # Return all prompts in the same label with no parameters
        candidate_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()
        return candidate_prompts

    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        label = self.get_label_from_prompt(prompt)
        candidate_prompts = self.find_candidate_prompts_no_params(label)

        # Retrieve probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'].get(cp, 0) for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if len(candidate_prompts) == 0 or len(normalized_probs) == 0:
            return []

        recommended_prompts = np.random.choice(candidate_prompts, 
                                               size=self.user_choice.numDeepDive, 
                                               replace=False, 
                                               p=normalized_probs)

        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numDeepDive, mode='recommendations')
        return recommended_prompts

    def exploration_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.get_label_from_prompt(prompt)

        # Find closest cluster
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            # pair is expected to be a string like "label1,label2"
            cluster_labels = pair.split(',')
            other_label = cluster_labels[0] if cluster_labels[1] == label else cluster_labels[1]
            if dist < min_distance:
                min_distance = dist
                closest_cluster_label = other_label

        candidate_prompts = self.find_candidate_prompts_no_params(closest_cluster_label)

        probs = [self.history_mgr.prompt_probs['no_params'].get(cp, 0) for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if len(candidate_prompts) == 0 or len(normalized_probs) == 0:
            return []

        recommended_prompts = np.random.choice(candidate_prompts, 
                                               size=self.user_choice.numExploration, 
                                               replace=False, 
                                               p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numExploration, mode='recommendations')

        return recommended_prompts

class ParamsRecommender(BaseRecommender):

    def find_candidate_prompts_params(self, lead_param: str) -> List[str]:
        df = self.history_mgr.prompts_mgr.df_prompts
        # Return prompts that have a single parameter equal to lead_param
        candidate_prompts = df[df['params'].apply(lambda x: x == [lead_param])]['prompts'].tolist()
        return candidate_prompts

    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        # Extract the leading parameter name from the prompt
        lead_param = df[df['prompts'] == prompt]['params'].iloc[0][0]
        lead_param_value = self.user_choice.parameters[lead_param]

        candidate_prompts = self.find_candidate_prompts_params(lead_param)

        # Ensure that each prompt has a probability entry for the given param value
        for cp in candidate_prompts:
            if lead_param not in self.history_mgr.prompt_probs['params'].get(cp, {}):
                self.history_mgr.prompt_probs['params'].setdefault(cp, {}).setdefault(lead_param, {})
            if lead_param_value not in self.history_mgr.prompt_probs['params'][cp][lead_param]:
                self.history_mgr.prompt_probs['params'][cp][lead_param][lead_param_value] = 1
        
        probs = [self.history_mgr.prompt_probs['params'][cp][lead_param][lead_param_value] for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if len(candidate_prompts) == 0 or len(normalized_probs) == 0:
            return []

        recommended_prompts = np.random.choice(candidate_prompts, 
                                               size=self.user_choice.numDeepDive, 
                                               replace=False, 
                                               p=normalized_probs)

        self.update_history_manager(recommended_prompts, params=[{lead_param: lead_param_value}]*self.user_choice.numDeepDive, mode='recommendations')

        return recommended_prompts

    def exploration_recommendations(self):
        # For parameter-based exploration, we mimic the NoParams BFS logic
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.get_label_from_prompt(prompt)

        # Here, exploration is the same cluster but no parameters
        # This is just a placeholder logic; you can tailor it based on your need
        candidate_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()
        probs = [self.history_mgr.prompt_probs['no_params'].get(cp, 0) for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if len(candidate_prompts) == 0 or len(normalized_probs) == 0:
            return []

        recommended_prompts = np.random.choice(candidate_prompts, 
                                               size=self.user_choice.numExploration, 
                                               replace=False, 
                                               p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numExploration, mode='recommendations')

        return recommended_prompts

# Example Usage
# -------------
# Assuming df_prompts is a pandas DataFrame with columns ['prompts','labels','params']
# and cluster_distances is a dict with keys like "label1,label2" and values as distances.
# Also assuming prompt_probs, user_choice_params and prompts_mgr are defined elsewhere.

"""
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.deep_dive_recommendations())
print(pr.exploration_recommendations())
"""
