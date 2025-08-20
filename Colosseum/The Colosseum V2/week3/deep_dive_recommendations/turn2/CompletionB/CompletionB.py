import numpy as np
from typing import List, Dict, Any

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager
    
    def deep_dive_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def exploration_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        if not probs or sum(probs) == 0:
            print("Total probability for the cluster is zero or empty, cannot sample.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts: List[str], params: List[Any], mode: str):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def find_label_for_prompt(self, df, prompt: str) -> Any:
        """Find the label associated with a given prompt."""
        match_indices = df[df['prompts'] == prompt].index
        if match_indices.empty:
            raise ValueError(f"No entry found for prompt: {prompt}")
        return df.loc[match_indices[0], 'labels']

    def find_closest_cluster_label(self, label: Any) -> Any:
        """
        Find the closest cluster label to the given label using cluster distances.
        """
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        if not relevant_distances:
            return None
        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                labels_pair = pair.split(',')
                # Identify the label that is not the current label
                closest_cluster_label = labels_pair[0] if labels_pair[1] == str(label) else labels_pair[1]
        return closest_cluster_label

class NoParamsRecommender(BaseRecommender):

    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.find_label_for_prompt(df, prompt)
        
        # Filter candidate prompts with the same label and no parameters
        candidate_prompts_df = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]
        candidate_prompts = candidate_prompts_df['prompts'].tolist()

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'].get(prompt, 0) for prompt in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if not normalized_probs:
            return []
        
        # Choose recommended prompts based on calculated probabilities
        recommended_prompts = np.random.choice(candidate_prompts, size=min(self.user_choice.numDeepDive, len(candidate_prompts)), replace=False, p=normalized_probs)
        
        # Update history manager with the chosen prompts
        self.update_history_manager(recommended_prompts, params=[None]*len(recommended_prompts), mode='recommendations')

        return recommended_prompts

    def exploration_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.find_label_for_prompt(df, prompt)
        
        # Find the closest cluster label
        closest_cluster_label = self.find_closest_cluster_label(label)
        if not closest_cluster_label:
            print("No closest cluster label found.")
            return []
        
        # Filter candidate prompts in the closest cluster with no parameters
        candidate_prompts_df = df[(df['labels'] == closest_cluster_label) & (df['params'].apply(lambda x: len(x) == 0))]
        candidate_prompts = candidate_prompts_df['prompts'].tolist()

        # If no candidate prompts are found in the closest cluster
        if not candidate_prompts:
            print("No candidate prompts found for exploration.")
            return []

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'].get(prompt, 0) for prompt in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if not normalized_probs:
            return []

        # Choose recommended prompts based on calculated probabilities
        recommended_prompts = np.random.choice(candidate_prompts, size=min(self.user_choice.numExploration, len(candidate_prompts)), replace=False, p=normalized_probs)
        
        # Update history manager with the chosen prompts
        self.update_history_manager(recommended_prompts, params=[None]*len(recommended_prompts), mode='recommendations')
        
        return recommended_prompts


class ParamsRecommender(BaseRecommender):
    
    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        # Check if the prompt exists in the DataFrame
        relevant_row = df[df['prompts'] == prompt]
        if relevant_row.empty:
            print(f"No data found for prompt: {prompt}")
            return []
        
        # Extract the first parameter of the prompt
        param_list = relevant_row.iloc[0]['params']
        if not param_list:
            print(f"No parameters found for prompt: {prompt}")
            return []
        lead_param = param_list[0]
        
        # Retrieve the user-provided value for the lead_param
        lead_param_value = self.user_choice.parameters.get(lead_param, None)
        if lead_param_value is None:
            print(f"No value provided for parameter: {lead_param}")
            return []
        
        # Filter candidate prompts that share the same parameter
        candidate_prompts_df = df[(df['params'].apply(lambda x: x == [lead_param]))]
        candidate_prompts = candidate_prompts_df['prompts'].tolist()

        # Update prompt probabilities dictionary for missing parameter values
        for cp in candidate_prompts:
            if lead_param_value not in self.history_mgr.prompt_probs['params'].setdefault(cp, {}).setdefault(lead_param, {}):
                self.history_mgr.prompt_probs['params'][cp][lead_param][lead_param_value] = 1

        # Calculate probabilities for candidate prompts based on parameter values
        probs = [self.history_mgr.prompt_probs['params'][cp][lead_param].get(lead_param_value, 0) for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if not normalized_probs:
            return []

        # Choose recommended prompts based on calculated probabilities
        recommended_prompts = np.random.choice(candidate_prompts, size=min(self.user_choice.numDeepDive, len(candidate_prompts)), replace=False, p=normalized_probs)
        
        # Update history manager with the chosen prompts
        self.update_history_manager(recommended_prompts, params=[{lead_param: lead_param_value}]*len(recommended_prompts), mode='recommendations')

        return recommended_prompts

    def exploration_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.find_label_for_prompt(df, prompt)
        
        # Filter candidate prompts within the same label but without parameters
        candidate_prompts_df = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]
        candidate_prompts = candidate_prompts_df['prompts'].tolist()

        if not candidate_prompts:
            print("No candidate prompts found for exploration.")
            return []

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'].get(cp, 0) for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        if not normalized_probs:
            return []

        # Choose recommended prompts based on calculated probabilities
        recommended_prompts = np.random.choice(candidate_prompts, size=min(self.user_choice.numExploration, len(candidate_prompts)), replace=False, p=normalized_probs)
        
        # Update history manager with the chosen prompts
        self.update_history_manager(recommended_prompts, params=[None]*len(recommended_prompts), mode='recommendations')

        return recommended_prompts


# Usage:
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.deep_dive_recommendations())
print(pr.exploration_recommendations())
