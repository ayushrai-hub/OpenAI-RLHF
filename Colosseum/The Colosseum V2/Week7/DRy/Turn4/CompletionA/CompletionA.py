from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import numpy as np

class MainRecommender(ABC):
    def __init__(self, user_selection: 'UserSelection', history_manager: 'HistoryLogger'):
        self.user_selection = user_selection
        self.history_manager = history_manager
        self.df_prompts = history_manager.prompts_manager.df_prompts

    @abstractmethod
    def give_recommendation_dfs(self) -> List[str]:
        pass

    @abstractmethod
    def give_recommendation_bfs(self) -> List[str]:
        pass

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        """Normalize probabilities to sum to 1."""
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the group is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def _get_current_label(self) -> str:
        """Extract label for the current prompt from DataFrame."""
        return self.df_prompts[self.df_prompts['prompts'] == self.user_selection.prompt]['labels'].iloc[0]

# Common functionality extracted to a mixin
class PromptRecommendationMixin:
    def _get_possible_prompts(self, df_filter: callable, prob_key: str) -> tuple[List[str], List[float]]:
        """Extract possible prompts and their probabilities based on filter criteria."""
        possible_prompts = self.df_prompts[df_filter(self.df_prompts)]['prompts'].tolist()
        probs = [self.history_manager.prompt_probabilities[prob_key][prompt] 
                for prompt in possible_prompts]
        return possible_prompts, probs

    def _sample_prompts(self, possible_prompts: List[str], probs: List[float], 
                       size: int, params: List[Optional[Dict]]) -> List[str]:
        """Sample prompts based on normalized probabilities."""
        standardized_probs = self.standardize_probabilities(probs)
        recommended_prompts = np.random.choice(
            possible_prompts, 
            size=size, 
            replace=False, 
            p=standardized_probs
        ).tolist()
        self.history_manager.update_prompt_probabilities(
            recommended_prompts, 
            params=params, 
            mode='recommendations'
        )
        return recommended_prompts

class NoParamsRecommendation(MainRecommender, PromptRecommendationMixin):
    def give_recommendation_dfs(self) -> List[str]:
        label = self._get_current_label()
        df_filter = lambda df: (df.labels == label) & (df.params.apply(len) == 0)
        possible_prompts, probs = self._get_possible_prompts(df_filter, 'no_params')
        return self._sample_prompts(
            possible_prompts, 
            probs, 
            self.user_selection.numDeepDive, 
            [None] * self.user_selection.numDeepDive
        )

    def give_recommendation_bfs(self) -> List[str]:
        label = self._get_current_label()
        relevant_distances = {
            pair: dist for pair, dist in self.history_manager.prompts_manager.cluster_distances.items() 
            if label in pair
        }
        
        closest_cluster_label = min(
            relevant_distances.items(), 
            key=lambda x: x[1],
            default=(None, float('inf'))
        )[0]
        if closest_cluster_label:
            closest_cluster_label = (closest_cluster_label.split(',')[0] 
                                  if closest_cluster_label.split(',')[1] == label 
                                  else closest_cluster_label.split(',')[1])

        df_filter = lambda df: (df.labels == closest_cluster_label) & (df.params.apply(len) == 0)
        possible_prompts, probs = self._get_possible_prompts(df_filter, 'no_params')
        return self._sample_prompts(
            possible_prompts, 
            probs, 
            self.user_selection.numExploration, 
            [None] * self.user_selection.numExploration
        )

class ParamRecommendation(MainRecommender, PromptRecommendationMixin):
    def give_recommendation_dfs(self) -> List[str]:
        prompt = self.user_selection.prompt
        # Corrected to match original: accessing first param from params list
        key_param = self.df_prompts[self.df_prompts['prompts'] == prompt]['params'].iloc[0][0]
        key_param_value = self.user_selection.parameters[key_param]
        
        df_filter = lambda df: df['params'].apply(lambda x: str(x) == str([key_param]))
        possible_prompts, _ = self._get_possible_prompts(df_filter, 'params')
        
        for p in possible_prompts:
            param_dict = self.history_manager.prompt_probabilities['params'][p][key_param]
            param_dict.setdefault(key_param_value, 1)
        
        probs = [self.history_manager.prompt_probabilities['params'][p][key_param][key_param_value] 
                for p in possible_prompts]
        
        return self._sample_prompts(
            possible_prompts, 
            probs, 
            self.user_selection.numDeepDive, 
            [{key_param: key_param_value}] * self.user_selection.numDeepDive
        )

    def give_recommendation_bfs(self) -> List[str]:
        label = self._get_current_label()
        df_filter = lambda df: (df.labels == label) & (df.params.apply(len) == 0)
        possible_prompts, probs = self._get_possible_prompts(df_filter, 'no_params')
        return self._sample_prompts(
            possible_prompts, 
            probs, 
            self.user_selection.numExploration, 
            [None] * self.user_selection.numExploration
        )

# Usage (assuming HistoryLogger, UserSelection, and required variables are defined)
history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)
print(user_selection_params.prompt)
print(param_rec.give_recommendation_dfs())
print(param_rec.give_recommendation_bfs())
