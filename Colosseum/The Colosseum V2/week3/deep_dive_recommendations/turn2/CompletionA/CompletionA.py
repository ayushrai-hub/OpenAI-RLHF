from typing import List, Dict, Any
import numpy as np

class BaseRecommender:
    def __init__(self, user_choice, history_mgr):
        self.user_choice = user_choice
        self.history_mgr = history_mgr
        self.df = history_mgr.prompts_mgr.df_prompts
        self.prompt = user_choice.prompt

    def deep_dive_recommendations(self):
        candidate_prompts = self.find_candidate_prompts_deep_dive()
        if not candidate_prompts:
            print("No candidate prompts found for deep dive recommendations.")
            return []
        probs = self.calculate_probabilities(candidate_prompts, mode='deep_dive')
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(
            candidate_prompts,
            size=self.user_choice.numDeepDive,
            replace=False,
            p=normalized_probs
        )
        self.update_history_manager(
            recommended_prompts,
            params=self.get_params_for_recommendations(recommended_prompts, mode='deep_dive'),
            mode='recommendations'
        )
        return recommended_prompts

    def exploration_recommendations(self):
        candidate_prompts = self.find_candidate_prompts_exploration()
        if not candidate_prompts:
            print("No candidate prompts found for exploration recommendations.")
            return []
        probs = self.calculate_probabilities(candidate_prompts, mode='exploration')
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(
            candidate_prompts,
            size=self.user_choice.numExploration,
            replace=False,
            p=normalized_probs
        )
        self.update_history_manager(
            recommended_prompts,
            params=self.get_params_for_recommendations(recommended_prompts, mode='exploration'),
            mode='recommendations'
        )
        return recommended_prompts

    def get_prompt_label(self, prompt):
        label_series = self.df[self.df['prompts'] == prompt]['labels']
        if label_series.empty:
            raise ValueError(f"No label found for prompt: {prompt}")
        return label_series.iloc[0]

    def normalize_probabilities(self, probs) -> List[float]:
        if not probs:
            print("No probabilities provided, cannot normalize.")
            return []
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability is zero, cannot normalize.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts, params, mode):
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

    # The following methods will be implemented in subclasses
    def find_candidate_prompts_deep_dive(self):
        raise NotImplementedError

    def find_candidate_prompts_exploration(self):
        raise NotImplementedError

    def calculate_probabilities(self, candidate_prompts, mode):
        raise NotImplementedError

    def get_params_for_recommendations(self, recommended_prompts, mode):
        raise NotImplementedError

class NoParamsRecommender(BaseRecommender):
    def find_candidate_prompts_deep_dive(self):
        label = self.get_prompt_label(self.prompt)
        candidate_prompts = self.df[
            (self.df['labels'] == label) &
            (self.df['params'].apply(len) == 0)
        ]['prompts'].tolist()
        return candidate_prompts

    def find_candidate_prompts_exploration(self):
        # Find the closest cluster label
        label = self.get_prompt_label(self.prompt)
        relevant_distances = {
            pair: dist
            for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items()
            if label in pair
        }
        if not relevant_distances:
            print(f"No relevant cluster distances found for label: {label}")
            return []
        closest_cluster_label = self.get_closest_cluster_label(relevant_distances, label)
        candidate_prompts = self.df[
            (self.df['labels'] == closest_cluster_label) &
            (self.df['params'].apply(len) == 0)
        ]['prompts'].tolist()
        return candidate_prompts

    def calculate_probabilities(self, candidate_prompts, mode):
        probs = [self.history_mgr.prompt_probs['no_params'].get(prompt, 1) for prompt in candidate_prompts]
        return probs

    def get_params_for_recommendations(self, recommended_prompts, mode):
        return [None] * len(recommended_prompts)

    def get_closest_cluster_label(self, relevant_distances, label):
        min_distance = float('inf')
        closest_cluster_label = None
        for pair_str, dist in relevant_distances.items():
            pair = tuple(pair_str.split(','))
            if dist < min_distance:
                min_distance = dist
                closest_cluster_label = pair[0] if pair[1] == label else pair[1]
        return closest_cluster_label

class ParamsRecommender(BaseRecommender):
    def find_candidate_prompts_deep_dive(self):
        # Get the leading parameter of the current prompt
        params_series = self.df[self.df['prompts'] == self.prompt]['params']
        if params_series.empty or not params_series.iloc[0]:
            print(f"No parameters found for prompt: {self.prompt}")
            return []
        lead_param = params_series.iloc[0][0]  # Assuming the first parameter is the lead
        candidate_prompts = self.df[
            self.df['params'].apply(lambda params: params and params[0] == lead_param)
        ]['prompts'].tolist()
        return candidate_prompts

    def find_candidate_prompts_exploration(self):
        # Use the same exploration strategy as NoParamsRecommender
        label = self.get_prompt_label(self.prompt)
        candidate_prompts = self.df[
            (self.df['labels'] == label) &
            (self.df['params'].apply(len) == 0)
        ]['prompts'].tolist()
        return candidate_prompts

    def calculate_probabilities(self, candidate_prompts, mode):
        if mode == 'deep_dive':
            # Get the leading parameter of the current prompt
            params_series = self.df[self.df['prompts'] == self.prompt]['params']
            lead_param = params_series.iloc[0][0]
            lead_param_value = self.user_choice.parameters[lead_param]
            probs = []
            for prompt in candidate_prompts:
                param_probs = self.history_mgr.prompt_probs['params'].get(prompt, {})
                lead_param_probs = param_probs.get(lead_param, {})
                prob = lead_param_probs.get(lead_param_value, 1)
                probs.append(prob)
            return probs
        else:
            # For exploration, use no_params probabilities
            probs = [self.history_mgr.prompt_probs['no_params'].get(prompt, 1) for prompt in candidate_prompts]
            return probs

    def get_params_for_recommendations(self, recommended_prompts, mode):
        if mode == 'deep_dive':
            params_series = self.df[self.df['prompts'] == self.prompt]['params']
            lead_param = params_series.iloc[0][0]
            lead_param_value = self.user_choice.parameters[lead_param]
            return [{lead_param: lead_param_value} for _ in recommended_prompts]
        else:
            return [None] * len(recommended_prompts)

    def get_prompt_label(self, prompt):
        # If the label is already fetched, return it directly
        return super().get_prompt_label(prompt)

# Usage Example
# Assuming that user_choice_params, prompts_mgr, ORG_ID, and ID are already defined
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)

# For ParamsRecommender
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print("Deep Dive Recommendations:")
print(pr.deep_dive_recommendations())
print("Exploration Recommendations:")
print(pr.exploration_recommendations())

# For NoParamsRecommender
npr = NoParamsRecommender(user_choice=user_choice_no_params, history_mgr=history_mgr)
print("Deep Dive Recommendations:")
print(npr.deep_dive_recommendations())
print("Exploration Recommendations:")
print(npr.exploration_recommendations())
