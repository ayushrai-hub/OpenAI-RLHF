from typing import List, Any
import numpy as np
from pydantic import BaseModel
class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend_dfs(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def recommend_bfs(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    # Helper method to filter prompts based on a condition
    def filter_prompts(self, condition) -> List[str]:
        df = self.history_mgr.prompts_mgr.df_prompts
        return df[condition]['prompts'].tolist()

    # Helper method to update the history manager with recommendations
    def update_history(self, recommended_prompts: List[str], params: List[Any], mode: str = 'recommendations'):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

class NoParamsRecommender(BaseRecommender):
    def recommend_dfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        
        condition = (df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))
        candidate_prompts = self.filter_prompts(condition)
        
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)
        
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs)
        self.update_history(recommended_prompts, params=[None] * self.user_choice.numDeepDive)
        
        return recommended_prompts

    def recommend_bfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        
        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                labels = pair.split(',')
                closest_cluster_label = labels[0] if labels[1] == label else labels[1]
        
        condition = (df['labels'] == closest_cluster_label) & (df['params'].apply(lambda x: len(x) == 0))
        candidate_prompts = self.filter_prompts(condition)
        
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)
        
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numExploration, replace=False, p=normalized_probs)
        self.update_history(recommended_prompts, params=[None] * self.user_choice.numExploration)
        
        return recommended_prompts

class ParamsRecommender(BaseRecommender):
    def recommend_dfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df[df['prompts'] == prompt]['params'].str[0].iloc[0]  # taking the first param if multiple
        
        condition = df['params'].apply(lambda x: str(x) == str([lead_param]))
        candidate_prompts = self.filter_prompts(condition)
        
        lead_param_value = self.user_choice.parameters[lead_param]
       
        for p in candidate_prompts:
            if lead_param_value not in self.history_mgr.prompt_probs['params'][p][lead_param]:
                self.history_mgr.prompt_probs['params'][p][lead_param][lead_param_value] = 1
        probs = [self.history_mgr.prompt_probs['params'][p][lead_param][lead_param_value] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)
        
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs)
        self.update_history(recommended_prompts, params=[{lead_param: lead_param_value}] * self.user_choice.numDeepDive)
        
        return recommended_prompts

    def recommend_bfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        
        condition = (df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))
        candidate_prompts = self.filter_prompts(condition)
        
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)
        
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numExploration, replace=False, p=normalized_probs)
        self.update_history(recommended_prompts, params=[None] * self.user_choice.numExploration)
        
        return recommended_prompts

# Assuming instantiation matches your setup
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)

pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend_dfs())
print(pr.recommend_bfs())
