import numpy as np
from typing import List, Dict, Any
from pydantic import BaseModel

class MainRecommender(BaseModel):
    user_selection: Any  # Substitute with your actual UserSelection type
    history_manager: Any  # Substitute with your actual HistoryLogger type

    def give_detailed_recommendation(self):
        """
        This method is analogous to DFS: 
        It stays within the same label/cluster (or same conditions) and dives deeper.
        """
        raise NotImplementedError("Subclasses should implement.")

    def give_general_recommendation(self):
        """
        This method is analogous to BFS: 
        It explores near or adjacent labels/clusters (or widened conditions).
        """
        raise NotImplementedError("Subclasses should implement.")

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        """
        Normalize a list of probabilities so they sum to 1.
        If the sum is zero, print a warning and return an empty list.
        """
        if not probs:
            print("No probabilities provided, returning an empty list.")
            return []
        
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability is zero, cannot standardize. Returning empty list.")
            return []
        
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, 
                               recommended_prompts: List[str], 
                               params: List[Dict[str, Any]], 
                               mode: str):
        """
        Encapsulate updates to the history manager to avoid repetition.
        """
        self.history_manager.update_prompt_probabilities(
            recommended_prompts, 
            params=params,
            mode=mode
        )

    @property
    def prompts_df(self):
        """
        Convenient property to access the DataFrame of prompts from history_manager’s prompts_manager.
        Adjust if your actual code references it differently.
        """
        return self.history_manager.prompts_manager.df_prompts


class NoParamsRecommendation(MainRecommender):
    def give_detailed_recommendation(self) -> List[str]:
        """
        DFS-like approach: 
        Stay within the same label as user_selection.prompt.
        """
        df = self.prompts_df
        
        # Obtain the label for the current user_selection.prompt
        current_prompt_label = df.loc[df['prompts'] == self.user_selection.prompt, 'labels'].iloc[0]
        
        # Filter prompts with the same label and no params
        matching_prompts = df[
            (df['labels'] == current_prompt_label) &
            (df['params'].apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()

        # Compute probabilities
        probs = [self.history_manager.prompt_probabilities['no_params'][p] for p in matching_prompts]
        standardized_probs = self.standardize_probabilities(probs)

        # Sample the recommended prompts
        recommended_prompts = np.random.choice(
            matching_prompts, 
            size=self.user_selection.numDeepDive, 
            replace=False, 
            p=standardized_probs
        )

        # Update history
        self.update_history_manager(
            recommended_prompts=recommended_prompts,
            params=[None]*self.user_selection.numDeepDive,
            mode='recommendations'
        )

        return recommended_prompts

    def give_general_recommendation(self) -> List[str]:
        """
        BFS-like approach:
        Move to the closest cluster by distance from the current prompt's label.
        """
        df = self.prompts_df
        
        # Get current prompt's label
        current_prompt_label = df.loc[df['prompts'] == self.user_selection.prompt, 'labels'].iloc[0]
        
        # Find cluster with minimum distance to current prompt's label
        cluster_distances = self.history_manager.prompts_manager.cluster_distances

        # Filter cluster distances to only relevant neighbors
        relevant_distances = {
            pair: dist for pair, dist in cluster_distances.items() 
            if current_prompt_label in pair
        }

        min_distance = float('inf')
        closest_cluster_label = None

        # Format of pair in cluster_distances might be something like "labelA,labelB"
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                # Determine which label in the pair is not current_prompt_label
                labels_in_pair = pair.split(',')
                if labels_in_pair[0] == current_prompt_label:
                    closest_cluster_label = labels_in_pair[1]
                else:
                    closest_cluster_label = labels_in_pair[0]

        # Filter prompts from the closest cluster label that have no params
        matching_prompts = df[
            (df['labels'] == closest_cluster_label) &
            (df['params'].apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()

        probs = [self.history_manager.prompt_probabilities['no_params'][p] for p in matching_prompts]
        standardized_probs = self.standardize_probabilities(probs)

        recommended_prompts = np.random.choice(
            matching_prompts, 
            size=self.user_selection.numExploration, 
            replace=False, 
            p=standardized_probs
        )

        self.update_history_manager(
            recommended_prompts=recommended_prompts,
            params=[None]*self.user_selection.numExploration,
            mode='recommendations'
        )

        return recommended_prompts


class ParamRecommendation(MainRecommender):
    def give_detailed_recommendation(self) -> List[str]:
        """
        DFS-like approach for parameters:
        Focus on prompts with param that matches the user's chosen parameter.
        """
        df = self.prompts_df
        
        # Find the key param of the current prompt.
        # Assuming each prompt with params has them in a list, we'll take the first param.
        # Adjust logic to match your actual data structure.
        current_prompt_params = df.loc[df['prompts'] == self.user_selection.prompt, 'params'].iloc[0]
        if not current_prompt_params:
            raise ValueError(f"No params found for prompt: {self.user_selection.prompt}")
        
        key_param = current_prompt_params[0]  # pick first param as "key"

        # The user_selection must contain a dictionary for parameters
        # e.g. user_selection.parameters = {'param_name': 'param_value'}
        key_param_value = self.user_selection.parameters[key_param]

        # Filter prompts that have the same key_param
        matching_prompts = df[
            df['params'].apply(lambda p_list: p_list == [key_param])
        ]['prompts'].tolist()

        # Ensure probability structure is defined for each prompt with each param value
        for p in matching_prompts:
            param_probs = self.history_manager.prompt_probabilities['params'].setdefault(p, {})
            param_probs.setdefault(key_param, {})
            if key_param_value not in param_probs[key_param]:
                param_probs[key_param][key_param_value] = 1

        # Compute probabilities
        probs = [
            self.history_manager.prompt_probabilities['params'][p][key_param][key_param_value] 
            for p in matching_prompts
        ]
        standardized_probs = self.standardize_probabilities(probs)

        recommended_prompts = np.random.choice(
            matching_prompts, 
            size=self.user_selection.numDeepDive, 
            replace=False, 
            p=standardized_probs
        )

        # Update history with param info
        param_info_list = [{key_param: key_param_value} for _ in range(self.user_selection.numDeepDive)]
        self.update_history_manager(
            recommended_prompts=recommended_prompts,
            params=param_info_list,
            mode='recommendations'
        )

        return recommended_prompts

    def give_general_recommendation(self) -> List[str]:
        """
        BFS-like approach if you want to transition from param-based to no-param or a different param set.
        For simplicity, it's similar to NoParamsRecommendation BFS, but you can customize.
        """
        df = self.prompts_df

        # Get label
        current_prompt_label = df.loc[df['prompts'] == self.user_selection.prompt, 'labels'].iloc[0]
        
        # Move to a different nearby cluster or label (like BFS)
        cluster_distances = self.history_manager.prompts_manager.cluster_distances
        relevant_distances = {
            pair: dist for pair, dist in cluster_distances.items()
            if current_prompt_label in pair
        }

        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                labels_in_pair = pair.split(',')
                closest_cluster_label = labels_in_pair[1] if labels_in_pair[0] == current_prompt_label else labels_in_pair
