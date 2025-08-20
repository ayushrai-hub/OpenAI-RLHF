from typing import List, Any
import numpy as np


class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def deep_dive_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def exploration_recommendations(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs: List[float]) -> List[float]:
        """Normalize a list of probabilities."""
        if not probs or sum(probs) == 0:
            print("Total probability is zero or empty; cannot sample.")
            return []
        total_prob = sum(probs)
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts: List[str], params: Any, mode: str):
        """Update the history manager with the recommended prompts."""
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    def find_candidate_prompts(self, filter_condition) -> List[str]:
        """Find candidate prompts based on a filter condition."""
        df = self.history_mgr.prompts_mgr.df_prompts
        return df[df.apply(filter_condition, axis=1)]['prompts'].tolist()

    def calculate_probabilities_no_params(self, candidate_prompts: List[str]) -> List[float]:
        """Calculate probabilities for no-params prompts."""
        return [self.history_mgr.prompt_probs['no_params'][prompt] for prompt in candidate_prompts]

    def calculate_probabilities_with_params(self, candidate_prompts: List[str], lead_param: str, lead_param_value: Any) -> List[float]:
        """Calculate probabilities for prompts with parameters."""
        probs = []
        for prompt in candidate_prompts:
            if lead_param_value not in self.history_mgr.prompt_probs['params'][prompt][lead_param]:
                self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value] = 1
            probs.append(self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value])
        return probs


class NoParamsRecommender(BaseRecommender):
    def deep_dive_recommendations(self):
        # Get the label of the current prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == self.user_choice.prompt]['labels'].iloc[0]

        # Find candidate prompts with no params and the same label
        candidate_prompts = self.find_candidate_prompts(
            lambda row: row['labels'] == label and len(row['params']) == 0
        )

        # Calculate probabilities and recommend prompts
        probs = self.calculate_probabilities_no_params(candidate_prompts)
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(
            candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs
        )

        # Update history manager and return recommendations
        self.update_history_manager(recommended_prompts, params=[None] * self.user_choice.numDeepDive, mode='recommendations')
        return recommended_prompts

    def exploration_recommendations(self):
        # Get the label of the current prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == self.user_choice.prompt]['labels'].iloc[0]

        # Find the closest cluster label
        relevant_distances = {
            pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair
        }
        closest_cluster_label = min(
            relevant_distances, key=lambda pair: relevant_distances[pair]
        ).replace(label, '').strip(',')

        # Find candidate prompts with no params and closest cluster label
        candidate_prompts = self.find_candidate_prompts(
            lambda row: row['labels'] == closest_cluster_label and len(row['params']) == 0
        )

        # Calculate probabilities and recommend prompts
        probs = self.calculate_probabilities_no_params(candidate_prompts)
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(
            candidate_prompts, size=self.user_choice.numExploration, replace=False, p=normalized_probs
        )

        # Update history manager and return recommendations
        self.update_history_manager(recommended_prompts, params=[None] * self.user_choice.numExploration, mode='recommendations')
        return recommended_prompts


class ParamsRecommender(BaseRecommender):
    def deep_dive_recommendations(self):
        # Identify lead parameter
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df[df['prompts'] == self.user_choice.prompt]['params'].str[0].iloc[0]
        lead_param_value = self.user_choice.parameters[lead_param]

        # Find candidate prompts with the same lead parameter
        candidate_prompts = self.find_candidate_prompts(
            lambda row: str(row['params']) == str([lead_param])
        )

        # Calculate probabilities and recommend prompts
        probs = self.calculate_probabilities_with_params(candidate_prompts, lead_param, lead_param_value)
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(
            candidate_prompts, size=self.user_choice.numDeepDive, replace=False, p=normalized_probs
        )

        # Update history manager and return recommendations
        self.update_history_manager(
            recommended_prompts, params=[{lead_param: lead_param_value}] * self.user_choice.numDeepDive, mode='recommendations'
        )
        return recommended_prompts

    def exploration_recommendations(self):
        # Currently left as an exercise or duplicate if similar to NoParamsRecommender.
        pass


# Usage Example
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)

# Make recommendations
print(user_choice_params.prompt)
print(pr.deep_dive_recommendations())
