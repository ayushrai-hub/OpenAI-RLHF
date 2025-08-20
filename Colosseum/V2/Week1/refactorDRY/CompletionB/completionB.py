from typing import List, Dict, Any
import numpy as np
from pydantic import BaseModel

class MainRecommender(BaseModel):
    user_selection: UserSelection
    history_manager: HistoryLogger

    def detailed_recommendation(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def general_recommendation(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def standardize_probabilities(self, probs) -> List[float]:
        if not probs:
            print("Total probability for the group is zero, cannot sample.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def get_label_for_prompt(self, prompt):
        df = self.history_manager.prompts_manager.df_prompts
        return df[df['prompts'] == prompt]['labels'].iloc[0]

    def sample_prompts(self, possible_prompts, probs, size):
        standardized_probs = self.standardize_probabilities(probs)
        return np.random.choice(possible_prompts, size=size, replace=False, p=standardized_probs)

    def update_history(self, recommended_prompts, params):
        self.history_manager.update_prompt_probabilities(recommended_prompts, params=params, mode='recommendations')

class NoParamsRecommendation(MainRecommender):
    def detailed_recommendation(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = self.get_label_for_prompt(prompt)
        possible_prompts = df[(df.labels == label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_manager.prompt_probabilities['no_params'][p] for p in possible_prompts]
        recommended_prompts = self.sample_prompts(possible_prompts, probs, self.user_selection.numDeepDive)
        self.update_history(recommended_prompts, [None] * self.user_selection.numDeepDive)
        return recommended_prompts

    def general_recommendation(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = self.get_label_for_prompt(prompt)
        relevant_distances = {pair: dist for pair, dist in self.history_manager.prompts_manager.cluster_distances.items() if label in pair}
        closest_cluster_label = min(relevant_distances, key=relevant_distances.get).replace(label, '').replace(',', '')
        possible_prompts = df[(df.labels == closest_cluster_label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_manager.prompt_probabilities['no_params'][p] for p in possible_prompts]
        recommended_prompts = self.sample_prompts(possible_prompts, probs, self.user_selection.numExploration)
        self.update_history(recommended_prompts, [None] * self.user_selection.numExploration)
        return recommended_prompts

class ParamRecommendation(MainRecommender):
    def detailed_recommendation(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        key_param = df[df['prompts'] == prompt]['params'].iloc[0][0]
        possible_prompts = df[df['params'].apply(lambda x: str(x) == str([key_param]))]['prompts'].tolist()
        key_param_value = self.user_selection.parameters[key_param]
        
        for p in possible_prompts:
            if key_param_value not in self.history_manager.prompt_probabilities['params'][p][key_param]:
                self.history_manager.prompt_probabilities['params'][p][key_param][key_param_value] = 1
        
        probs = [self.history_manager.prompt_probabilities['params'][p][key_param][key_param_value] for p in possible_prompts]
        recommended_prompts = self.sample_prompts(possible_prompts, probs, self.user_selection.numDeepDive)
        self.update_history(recommended_prompts, [{key_param: key_param_value}] * self.user_selection.numDeepDive)
        return recommended_prompts

    def general_recommendation(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = self.get_label_for_prompt(prompt)
        possible_prompts = df[(df.labels == label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_manager.prompt_probabilities['no_params'][p] for p in possible_prompts]
        recommended_prompts = self.sample_prompts(possible_prompts, probs, self.user_selection.numExploration)
        self.update_history(recommended_prompts, [None] * self.user_selection.numExploration)
        return recommended_prompts

# Usage example
history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)
print(user_selection_params.prompt)
print(param_rec.detailed_recommendation())
print(param_rec.general_recommendation())
