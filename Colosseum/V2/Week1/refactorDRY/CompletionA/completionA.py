from typing import List, Dict, Any
import numpy as np
from pydantic import BaseModel

class MainRecommender(BaseModel):
    user_selection: UserSelection
    history_manager: HistoryLogger

    def get_prompt_label(self) -> str:
        """Get the label for the current prompt."""
        df = self.history_manager.prompts_manager.df_prompts
        return df[df['prompts'] == self.user_selection.prompt]['labels'].iloc[0]

    def detailed_recommendation(self):
        """Detailed (DFS) recommendation implementation."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def general_recommendation(self):
        """General (BFS) recommendation implementation."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def standardize_probabilities(self, probs) -> List[float]:
        """Standardize probability values."""
        if not probs:
            print("Empty probability list provided, cannot sample.")
            return []
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def sample_recommendations(self, possible_prompts: List[str], probs: List[float], 
                             sample_size: int, params: List[Any]) -> List[str]:
        """Sample recommendations and update history."""
        standardized_probs = self.standardize_probabilities(probs)
        if not standardized_probs:
            return []
        recommended_prompts = np.random.choice(possible_prompts, 
                                             size=min(sample_size, len(possible_prompts)), 
                                             replace=False, 
                                             p=standardized_probs)
        self.history_manager.update_prompt_probabilities(
            recommended_prompts, 
            params=params, 
            mode='recommendations'
        )
        return recommended_prompts.tolist()

class NoParamsRecommendation(MainRecommender):
    def detailed_recommendation(self):
        df = self.history_manager.prompts_manager.df_prompts
        current_label = self.get_prompt_label()
        
        # Get prompts with same label and no parameters
        possible_prompts = df[
            (df.labels == current_label) & 
            (df.params.apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()
        
        # Calculate probabilities
        probs = [self.history_manager.prompt_probabilities['no_params'][prompt] 
                for prompt in possible_prompts]
        
        return self.sample_recommendations(
            possible_prompts,
            probs,
            self.user_selection.numDeepDive,
            [None] * self.user_selection.numDeepDive
        )

    def general_recommendation(self):
        df = self.history_manager.prompts_manager.df_prompts
        current_label = self.get_prompt_label()
        
        # Find closest cluster
        relevant_distances = {
            pair: dist for pair, dist in 
            self.history_manager.prompts_manager.cluster_distances.items() 
            if current_label in pair
        }
        
        if not relevant_distances:
            return []
            
        min_distance = min(relevant_distances.values())
        closest_pair = [pair for pair, dist in relevant_distances.items() 
                       if dist == min_distance][0]
        closest_cluster_label = (closest_pair.split(',')[1] 
                               if closest_pair.split(',')[0] == current_label 
                               else closest_pair.split(',')[0])
        
        # Get prompts from closest cluster with no parameters
        possible_prompts = df[
            (df.labels == closest_cluster_label) & 
            (df.params.apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()
        
        # Calculate probabilities
        probs = [self.history_manager.prompt_probabilities['no_params'][prompt] 
                for prompt in possible_prompts]
        
        return self.sample_recommendations(
            possible_prompts,
            probs,
            self.user_selection.numExploration,
            [None] * self.user_selection.numExploration
        )

class ParamRecommendation(MainRecommender):
    def detailed_recommendation(self):
        df = self.history_manager.prompts_manager.df_prompts
        prompt = self.user_selection.prompt
        
        # Get the key parameter for the current prompt
        prompt_params = df[df['prompts'] == prompt]['params'].iloc[0]
        if not prompt_params:
            return []
        
        key_param = prompt_params[0]
        key_param_value = self.user_selection.parameters.get(key_param)
        if not key_param_value:
            return []
        
        # Get prompts with the same parameter
        possible_prompts = df[
            df['params'].apply(lambda x: str(x) == str([key_param]))
        ]['prompts'].tolist()
        
        # Initialize probabilities if needed and calculate
        for prompt in possible_prompts:
            if prompt not in self.history_manager.prompt_probabilities['params']:
                self.history_manager.prompt_probabilities['params'][prompt] = {}
            if key_param not in self.history_manager.prompt_probabilities['params'][prompt]:
                self.history_manager.prompt_probabilities['params'][prompt][key_param] = {}
            if key_param_value not in self.history_manager.prompt_probabilities['params'][prompt][key_param]:
                self.history_manager.prompt_probabilities['params'][prompt][key_param][key_param_value] = 1
        
        probs = [self.history_manager.prompt_probabilities['params'][prompt][key_param][key_param_value] 
                for prompt in possible_prompts]
        
        return self.sample_recommendations(
            possible_prompts,
            probs,
            self.user_selection.numDeepDive,
            [{key_param: key_param_value}] * self.user_selection.numDeepDive
        )

    def general_recommendation(self):
        df = self.history_manager.prompts_manager.df_prompts
        current_label = self.get_prompt_label()
        
        # Get prompts with same label and no parameters
        possible_prompts = df[
            (df.labels == current_label) & 
            (df.params.apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()
        
        # Calculate probabilities
        probs = [self.history_manager.prompt_probabilities['no_params'][prompt] 
                for prompt in possible_prompts]
        
        return self.sample_recommendations(
            possible_prompts,
            probs,
            self.user_selection.numExploration,
            [None] * self.user_selection.numExploration
        )

# Usage example
if __name__ == "__main__":
    history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
    param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)
    
    print("Selected prompt:", user_selection_params.prompt)
    print("Detailed recommendations:", param_rec.detailed_recommendation())
    print("General recommendations:", param_rec.general_recommendation())
