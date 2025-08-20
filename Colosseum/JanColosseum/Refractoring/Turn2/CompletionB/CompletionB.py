from typing import List, Dict, Tuple, Callable
import numpy as np

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend(self, find_candidates_func: Callable, num_to_recommend: int, params: Any) -> List[str]:
        """Generalized recommendation function for both DFS and BFS."""
        candidate_prompts = find_candidates_func()
        if not candidate_prompts:
            print("No candidate prompts found.")
            return []
        
        probs = self.calculate_probabilities(candidate_prompts)
        normalized_probs = self.normalize_probabilities(probs)
        if not normalized_probs:
            print("Could not normalize probabilities, returning an empty list.")
            return []
        
        recommended_prompts = np.random.choice(
            candidate_prompts, 
            size=min(num_to_recommend, len(candidate_prompts)), 
            replace=False, 
            p=normalized_probs
        )
        self.update_history_manager(recommended_prompts, params, mode='recommendations')
        return recommended_prompts

    def update_history_manager(self, recommended_prompts: List[str], params: List[Any], mode: str):
        """Abstraction for updating prompt recommendations in history manager."""
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        """Lookup probabilities for candidate prompts (to be implemented by subclasses)."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        """Normalize a list of probabilities."""
        total_prob = sum(probs)
        if total_prob == 0:
            return []
        return [prob / total_prob for prob in probs]

class NoParamsRecommender(BaseRecommender):
    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        """Fetch probabilities for candidate prompts in NoParamsRecommender."""
        return [self.history_mgr.prompt_probs['no_params'].get(prompt, 0) for prompt in candidate_prompts]

    def find_candidates_dfs(self) -> List[str]:
        """Find candidate prompts for DFS (deep dive) without parameters."""
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]  # Assuming unique prompts
        return df[(df['labels'] == label) & (df['params'].apply(len) == 0)]['prompts'].tolist()

    def find_candidates_bfs(self) -> List[str]:
        """Find candidate prompts for BFS (exploration) without parameters."""
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]
        
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        closest_cluster_label = min(
            relevant_distances.items(), key=lambda x: x[1], default=(None, None)
        )[0]
        if closest_cluster_label:
            closest_label = closest_cluster_label.split(',')[0] if closest_cluster_label.split(',')[1] == label else closest_cluster_label.split(',')[1]
            return df[(df['labels'] == closest_label) & (df['params'].apply(len) == 0)]['prompts'].tolist()
        return []

    def deep_dive_recommendations(self):
        return self.recommend(self.find_candidates_dfs, self.user_choice.numDeepDive, params=[None] * self.user_choice.numDeepDive)

    def exploration_recommendations(self):
        return self.recommend(self.find_candidates_bfs, self.user_choice.numExploration, params=[None] * self.user_choice.numExploration)


class ParamsRecommender(BaseRecommender):
    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        """Fetch probabilities for candidate prompts in ParamsRecommender."""
        lead_param = self.find_lead_param()
        lead_param_value = self.user_choice.parameters.get(lead_param)
        probs = []
        
        for prompt in candidate_prompts:
            param_probs = self.history_mgr.prompt_probs['params'].setdefault(prompt, {}).setdefault(lead_param, {})
            probs.append(param_probs.get(lead_param_value, 1))
        return probs

    def find_lead_param(self) -> str:
        """Extract the lead parameter from the current user prompt."""
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        return df.loc[df['prompts'] == prompt, 'params'].str[0].iloc[0]

    def find_candidates_dfs(self) -> List[str]:
        """Find candidate prompts for DFS (deep dive) with parameters."""
        lead_param = self.find_lead_param()
        df = self.history_mgr.prompts_mgr.df_prompts
        return df[df['params'].apply(lambda x: x == [lead_param])]['prompts'].tolist()

    def find_candidates_bfs(self) -> List[str]:
        """Find candidate prompts for BFS (exploration) with parameters by looking for no-param prompts."""
        no_params_recommender = NoParamsRecommender(self.user_choice, self.history_mgr)
        return no_params_recommender.find_candidates_bfs()

    def deep_dive_recommendations(self):
        lead_param = self.find_lead_param()
        lead_param_value = self.user_choice.parameters.get(lead_param)
        return self.recommend(self.find_candidates_dfs, self.user_choice.numDeepDive, params=[{lead_param: lead_param_value}] * self.user_choice.numDeepDive)

    def exploration_recommendations(self):
        return self.recommend(self.find_candidates_bfs, self.user_choice.numExploration, params=[None] * self.user_choice.numExploration)
