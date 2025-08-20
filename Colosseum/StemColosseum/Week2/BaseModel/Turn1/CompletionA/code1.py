from typing import List, Dict, Any

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def deep_dive_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def exploration_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs) -> List[float]:
        if not probs:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts, params, mode):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def find_candidate_prompts(self, filter_condition) -> List[str]:
        raise NotImplementedError("This method should be implemented by subclasses to define how to filter candidate prompts.")

    def calculate_probabilities(self, candidate_prompts) -> List[float]:
        raise NotImplementedError("This method should be implemented by subclasses to define how probabilities are calculated.")

class NoParamsRecommender(BaseRecommender):
    def find_candidate_prompts(self, filter_condition) -> List[str]:
        df = self.history_mgr.prompts_mgr.df_prompts
        return df[df.apply(filter_condition, axis=1)]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts) -> List[float]:
        return [self.history_mgr.prompt_probs['no_params'][prompt] for prompt in candidate_prompts]

    def deep_dive_recommendations(self):
        candidate_prompts = self.find_candidate_prompts(lambda row: row['labels'] == self.user_choice.prompt_label and len(row['params']) == 0)
        normalized_probs = self.normalize_probabilities(self.calculate_probabilities(candidate_prompts))
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numDeepDive, mode='recommendations')
        return recommended_prompts

    # Similar implementation for exploration_recommendations()

class ParamsRecommender(BaseRecommender):
    # Implementation following the pattern of NoParamsRecommender but specific to parameters handling.

# Similar to NoParamsRecommender but uses the user_choice parameters to find and recommend prompts.

# Usage Example
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.deep_dive_recommendations())
print(pr.exploration_recommendations())
