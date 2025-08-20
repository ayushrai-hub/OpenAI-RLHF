from typing import List, Dict, Any
import numpy as np

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend(self, mode: str) -> List[str]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        if mode == "deep_dive":
            label = df[df['prompts'] == prompt]['labels'].iloc[0]
            candidate_prompts = self.get_deep_dive_candidates(df, label)
        elif mode == "exploration":
            label = df[df['prompts'] == prompt]['labels'].iloc[0]
            closest_cluster_label = self.find_closest_cluster(label)
            candidate_prompts = self.get_exploration_candidates(df, closest_cluster_label)

        probabilities = self.calculate_probabilities(candidate_prompts, mode)
        normalized_probs = self.normalize_probabilities(probabilities)

        size = self.user_choice.numDeepDive if mode == "deep_dive" else self.user_choice.numExploration
        recommended_prompts = np.random.choice(candidate_prompts, size=size, replace=False, p=normalized_probs)
        params = [None] * size if isinstance(self, NoParamsRecommender) else [{k: self.user_choice.parameters[k]} for k in self.user_choice.parameters]
        
        self.update_history_manager(recommended_prompts, params, mode='recommendations')
        return recommended_prompts

    def normalize_probabilities(self, probs) -> List[float]:
        if not probs or sum(probs) == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts, params, mode):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def find_closest_cluster(self, label: str) -> str:
        relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
        closest_label = None
        min_distance = float('inf')
        for pair, dist in relevant_distances.items():
            other_label = pair.replace(label, '').replace(',', '')
            if dist < min_distance:
                min_distance, closest_label = dist, other_label
        return closest_label

    def get_deep_dive_candidates(self, df, label: str) -> List[str]:
        raise NotImplementedError("This method should be overridden by subclasses.")

    def get_exploration_candidates(self, df, closest_cluster_label: str) -> List[str]:
        return df[(df['labels'] == closest_cluster_label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts: List[str], mode: str) -> List[float]:
        raise NotImplementedError("This method should be overridden by subclasses.")


class NoParamsRecommender(BaseRecommender):
    def get_deep_dive_candidates(self, df, label: str) -> List[str]:
        return df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts: List[str], mode: str) -> List[float]:
        return [self.history_mgr.prompt_probs['no_params'].get(prompt, 1) for prompt in candidate_prompts]


class ParamsRecommender(BaseRecommender):
    def get_deep_dive_candidates(self, df, label: str) -> List[str]:
        lead_param = df[df['prompts'] == self.user_choice.prompt]['params'].str[0].iloc[0]
        return df[df['params'].apply(lambda x: str(x) == str([lead_param]))]['prompts'].tolist()

    def calculate_probabilities(self, candidate_prompts: List[str], mode: str) -> List[float]:
        lead_param = df[df['prompts'] == self.user_choice.prompt]['params'].str[0].iloc[0]
        lead_param_value = self.user_choice.parameters.get(lead_param)
        return [self.history_mgr.prompt_probs['params'][prompt][lead_param].get(lead_param_value, 1) for prompt in candidate_prompts]


# Usage Example
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend(mode="deep_dive"))
print(pr.recommend(mode="exploration"))
