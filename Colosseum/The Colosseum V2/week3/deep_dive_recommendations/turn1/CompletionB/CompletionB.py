from typing import List
import numpy as np

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def deep_dive_recommendations(self):
        """Retrieve deep dive recommendations. Implement in subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def exploration_recommendations(self):
        """Retrieve exploration recommendations. Implement in subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        if not probs:
            print("No probabilities to normalize, returning empty list.")
            return []
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts: List[str], params: List[dict], mode: str):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def get_prompt_label(self, prompt: str) -> str:
        df = self.history_mgr.prompts_mgr.df_prompts
        return df.loc[df['prompts'] == prompt, 'labels'].iloc[0]

class NoParamsRecommender(BaseRecommender):

    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.get_prompt_label(prompt)

        # Candidate prompts for deep dive (same cluster, no params)
        candidate_prompts = df[(df.labels == label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numDeepDive, mode='recommendations')
        return recommended_prompts

    def exploration_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.get_prompt_label(prompt)

        # Determine the closest cluster label
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        min_distance = float('inf')
        closest_cluster_label = None

        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                # Determine which label in the pair is the other cluster
                cluster_pair = pair.split(',')
                closest_cluster_label = cluster_pair[0] if cluster_pair[1] == label else cluster_pair[1]

        # Candidate prompts for exploration (closest cluster, no params)
        candidate_prompts = df[(df.labels == closest_cluster_label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numExploration, replace=False, p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numExploration, mode='recommendations')
        return recommended_prompts

class ParamsRecommender(BaseRecommender):

    def deep_dive_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Extract the lead parameter from the current prompt
        lead_param = df.loc[df['prompts'] == prompt, 'params'].iloc[0][0]
        candidate_prompts = df[df['params'].apply(lambda x: len(x) == 1 and x[0] == lead_param)]['prompts'].tolist()
        lead_param_value = self.user_choice.parameters[lead_param]

        # Ensure the lead param values exist in prompt_probs
        for cp in candidate_prompts:
            if lead_param_value not in self.history_mgr.prompt_probs['params'][cp][lead_param]:
                self.history_mgr.prompt_probs['params'][cp][lead_param][lead_param_value] = 1

        probs = [self.history_mgr.prompt_probs['params'][cp][lead_param][lead_param_value] for cp in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[{lead_param: lead_param_value}]*self.user_choice.numDeepDive, mode='recommendations')
        return recommended_prompts

    def exploration_recommendations(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = self.get_prompt_label(prompt)

        # Candidate prompts for exploration (same cluster, no params)
        candidate_prompts = df[(df.labels == label) & (df.params.apply(lambda x: len(x)) == 0)]['prompts'].tolist()
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)

        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numExploration, replace=False, p=normalized_probs)
        self.update_history_manager(recommended_prompts, params=[None]*self.user_choice.numExploration, mode='recommendations')
        return recommended_prompts


# Usage Example
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.deep_dive_recommendations())
print(pr.exploration_recommendations())
