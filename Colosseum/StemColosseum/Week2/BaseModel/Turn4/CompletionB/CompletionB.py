import numpy as np
from typing import List, Dict, Any

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend(self, deep_dive: bool):
        """General method for recommendation. Calls specific logic per subclass based on recommendation type (Deep Dive or Exploration)."""
        candidate_prompts = self.find_candidate_prompts(deep_dive)
        if not candidate_prompts:
            print("No candidate prompts found.")
            return []
        
        probs = self.calculate_probabilities(candidate_prompts)
        normalized_probs = self.normalize_probabilities(probs)
        
        num_recommendations = self.user_choice.numDeepDive if deep_dive else self.user_choice.numExploration
        recommended_prompts = np.random.choice(candidate_prompts, size=num_recommendations, replace=False, p=normalized_probs)
        
        params = self.get_params_for_recommendation(deep_dive, len(recommended_prompts))
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode='recommendations')

        return recommended_prompts

    def normalize_probabilities(self, probs) -> List[float]:
        if not probs:
            print("No probabilities found; returning empty list.")
            return []
        
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []

        return [prob / total_prob for prob in probs]

    def find_candidate_prompts(self, deep_dive: bool) -> List[str]:
        raise NotImplementedError("Must be implemented by subclasses to define filtering condition.")

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        raise NotImplementedError("Must be implemented by subclasses to calculate prompt probabilities.")

    def get_params_for_recommendation(self, deep_dive: bool, num_prompts: int) -> List[Dict[str, Any]]:
        """Returns params for prompts depending on the type of recommendation method."""
        return [None] * num_prompts

    
class NoParamsRecommender(BaseRecommender):

    def find_candidate_prompts(self, deep_dive: bool) -> List[str]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Find label corresponding to the given prompt
        label = df[df['prompts'] == prompt]['labels'].iloc[0]

        # If deep dive, find prompts within the same cluster and no params
        if deep_dive:
            return df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()
        
        # For exploration, find prompts from closest cluster
        return self._find_closest_cluster_prompts(label)

    def _find_closest_cluster_prompts(self, current_label: str) -> List[str]:
        df = self.history_mgr.prompts_mgr.df_prompts

        # Find closest cluster based on distances in the history manager
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if current_label in pair}
        
        min_distance = float('inf')
        closest_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                closest_label = pair.split(',')[0] if pair.split(',')[1] == current_label else pair.split(',')[1]

        # Return prompts from closest cluster, again only those with no parameters
        return df[(df['labels'] == closest_label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        return [self.history_mgr.prompt_probs['no_params'][prompt] for prompt in candidate_prompts]


class ParamsRecommender(BaseRecommender):

    def find_candidate_prompts(self, deep_dive: bool) -> List[str]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        if deep_dive:
            # Get the leading parameter from the prompt
            lead_param = df[df['prompts'] == prompt]['params'].str[0].iloc[0]
            return df[df['params'].apply(lambda x: str(x) == str([lead_param]))]['prompts'].tolist()
        else:
            # Exploration mode works similarly to NoParamsRecommender when exploration type is used
            label = df[df['prompts'] == prompt]['labels'].iloc[0]
            return self._find_closest_cluster_prompts(label)

    def _find_closest_cluster_prompts(self, current_label: str) -> List[str]:
        # Same logic as NoParamsRecommender for exploration
        df = self.history_mgr.prompts_mgr.df_prompts
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if current_label in pair}

        min_distance = float('inf')
        closest_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                closest_label = pair.split(',')[0] if pair.split(',')[1] == current_label else pair.split(',')[1]

        return df[(df['labels'] == closest_label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        lead_param = self.user_choice.prompt_parameters[0]  # Assuming the first parameter is to be used
        lead_param_value = self.user_choice.parameters.get(lead_param)

        for prompt in candidate_prompts:
            if lead_param_value not in self.history_mgr.prompt_probs['params'][prompt][lead_param]:
                self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value] = 1

        return [self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value] for prompt in candidate_prompts]

    def get_params_for_recommendation(self, deep_dive: bool, num_prompts: int) -> List[Dict[str, Any]]:
        if deep_dive:
            lead_param = self.user_choice.prompt_parameters[0]
            lead_param_value = self.user_choice.parameters.get(lead_param)
            return [{lead_param: lead_param_value}] * num_prompts
        return super().get_params_for_recommendation(deep_dive, num_prompts)


# Example usage
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)

# Assume user_choice_params is passed with appropriate fields, including `prompt` and `parameters`
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend(deep_dive=True))  # Deep Dive Recommendation
print(pr.recommend(deep_dive=False))  # Exploration Recommendation
