import numpy as np
from typing import List, Any, Callable

# =============================================================================
# Base class with common functionality and helpers
# =============================================================================

class MainRecommender(BaseModel):
    user_selection: UserSelection
    history_manager: HistoryLogger

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the group is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history(self, recommended_prompts: List[str], params: Any, mode: str = 'recommendations'):
        """
        A helper that wraps the history_manager update call.
        """
        self.history_manager.update_prompt_probabilities(
            recommended_prompts, params=[params] * len(recommended_prompts), mode=mode
        )

    def _get_label_from_prompt(self, prompt: str) -> str:
        """
        Looks up the label corresponding to the provided prompt.
        """
        df = self.history_manager.prompts_manager.df_prompts
        return df.loc[df['prompts'] == prompt, 'labels'].iloc[0]

    def _recommend(self,
                   possible_prompts: List[str],
                   probability_getter: Callable[[str], float],
                   sample_size: int,
                   params: Any) -> List[str]:
        """
        A helper method that, given a list of candidate prompts and a function to
        get their probability, standardizes the probabilities, samples the required
        number, and then updates the history.
        """
        # Get probabilities for each candidate
        probs = [probability_getter(p) for p in possible_prompts]
        standardized_probs = self.standardize_probabilities(probs)
        if not standardized_probs:
            return []  # nothing to sample if probabilities are empty
        # Randomly sample prompts using the standardized probabilities
        recommended_prompts = np.random.choice(possible_prompts, size=sample_size, replace=False, p=standardized_probs)
        self.update_history(list(recommended_prompts), params, mode='recommendations')
        return list(recommended_prompts)

    def give_recommendation_dfs(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def give_recommendation_bfs(self):
        raise NotImplementedError("Subclasses must implement this method.")


# =============================================================================
# NoParamsRecommendation class – recommendations for prompts with no parameters
# =============================================================================

class NoParamsRecommendation(MainRecommender):
    def give_recommendation_dfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts

        # Get the label for the current prompt
        label = self._get_label_from_prompt(prompt)
        # Filter prompts that have the same label and no parameters (empty list)
        possible_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

        # Use the stored probability for "no_params"
        probability_getter = lambda p: self.history_manager.prompt_probabilities['no_params'].get(p, 0)
        return self._recommend(possible_prompts,
                               probability_getter,
                               self.user_selection.numDeepDive,
                               params=None)

    def _get_closest_cluster_label(self, label: str) -> str:
        """
        Finds the label of the cluster that is closest to the given label
        based on the cluster distances dictionary.
        """
        cluster_distances = self.history_manager.prompts_manager.cluster_distances
        # Filter to pairs that contain the label
        relevant = {pair: dist for pair, dist in cluster_distances.items() if label in pair}
        min_distance = float('inf')
        closest = None
        for pair, dist in relevant.items():
            if dist < min_distance:
                min_distance = dist
                # pair format is "label1,label2"; pick the label that is not the given one.
                parts = pair.split(',')
                closest = parts[0] if parts[1] == label else parts[1]
        return closest

    def give_recommendation_bfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts

        label = self._get_label_from_prompt(prompt)
        # Find the closest cluster label to the current prompt’s label
        closest_label = self._get_closest_cluster_label(label)
        # Filter prompts that belong to that closest cluster and have no parameters
        possible_prompts = df[(df['labels'] == closest_label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

        probability_getter = lambda p: self.history_manager.prompt_probabilities['no_params'].get(p, 0)
        return self._recommend(possible_prompts,
                               probability_getter,
                               self.user_selection.numExploration,
                               params=None)


# =============================================================================
# ParamRecommendation class – recommendations for prompts with parameters
# =============================================================================

class ParamRecommendation(MainRecommender):
    def give_recommendation_dfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts

        # Locate the current prompt's row and extract the key parameter (assumed first element)
        row = df.loc[df['prompts'] == prompt]
        if row.empty:
            print("Prompt not found in the dataset.")
            return []
        key_param = row['params'].iloc[0][0]  # assuming the first parameter is the key

        # Filter prompts that have exactly the same key parameter as a single-item list
        possible_prompts = df[df['params'].apply(lambda x: x == [key_param])]['prompts'].tolist()

        # Look up the value of this parameter from the user's selection.
        key_param_value = self.user_selection.parameters.get(key_param)
        if key_param_value is None:
            print(f"Key parameter value for {key_param} not provided.")
            return []

        # Ensure that for each candidate prompt the probability dict has an entry for this parameter value.
        for p in possible_prompts:
            param_probs = self.history_manager.prompt_probabilities['params'].setdefault(p, {}).setdefault(key_param, {})
            if key_param_value not in param_probs:
                param_probs[key_param_value] = 1  # initialize with a default probability

        probability_getter = lambda p: self.history_manager.prompt_probabilities['params'][p][key_param].get(key_param_value, 0)
        return self._recommend(possible_prompts,
                               probability_getter,
                               self.user_selection.numDeepDive,
                               params={key_param: key_param_value})

    def give_recommendation_bfs(self):
        # For BFS in the parameterized case, we fall back on the no-parameters BFS approach.
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts

        label = self._get_label_from_prompt(prompt)
        # Filter prompts with the same label and no parameters.
        possible_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

        probability_getter = lambda p: self.history_manager.prompt_probabilities['no_params'].get(p, 0)
        return self._recommend(possible_prompts,
                               probability_getter,
                               self.user_selection.numExploration,
                               params=None)


# =============================================================================
# Example Usage
# =============================================================================

# Assuming that HistoryLogger, prompts_manager, ORG_ID, ID, and UserSelection (for example, user_selection_params)
# are defined elsewhere in your code, you can use the recommender classes as follows:

# history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
# param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)
# print("User prompt:", user_selection_params.prompt)
# print("DFS Recommendation:", param_rec.give_recommendation_dfs())
# print("BFS Recommendation:", param_rec.give_recommendation_bfs())
