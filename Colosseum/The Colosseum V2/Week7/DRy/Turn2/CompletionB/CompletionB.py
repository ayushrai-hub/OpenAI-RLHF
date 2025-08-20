from typing import List, Dict, Any
import numpy as np

class MainRecommender(BaseModel):
    user_selection: UserSelection
    history_manager: HistoryLogger

    def give_recommendation(self, mode: str, size: int) -> List[str]:
        """
        A unified method to give recommendations based on the mode.
        """
        df = self.history_manager.prompts_manager.df_prompts
        prompt = self.user_selection.prompt
        label = df[df['prompts'] == prompt]['labels'].iloc[0]

        if mode == 'dfs':
            possible_prompts = self.filter_prompts_dfs(df, label, prompt)
        elif mode == 'bfs':
            possible_prompts = self.filter_prompts_bfs(df, label)
        else:
            raise ValueError("Invalid mode. Use 'dfs' or 'bfs'.")

        probs = self.compute_probabilities(possible_prompts)
        normalized_probs = self.standardize_probabilities(probs)

        if not normalized_probs:
            return []

        recommended_prompts = np.random.choice(possible_prompts, size=size, replace=False, p=normalized_probs)
        params = self.create_params_list(size)
        self.update_history_manager(recommended_prompts, params, mode='recommendations')

        return recommended_prompts

    def filter_prompts_dfs(self, df, label, prompt) -> List[str]:
        """Filter prompts for a DFS recommendation."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def filter_prompts_bfs(self, df, label) -> List[str]:
        """Filter prompts for a BFS recommendation across clusters."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def compute_probabilities(self, prompts: List[str]) -> List[float]:
        """Calculate probabilities for a list of prompts."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def create_params_list(self, size: int) -> List[Any]:
        """Create a list of parameters for the history manager."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        if not probs:
            print("No probabilities available.")
            return []
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the group is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts, params, mode):
        """Update the history manager with the recommended prompts."""
        self.history_manager.update_prompt_probabilities(recommended_prompts, params=params, mode=mode)


class NoParamsRecommendation(MainRecommender):
    def filter_prompts_dfs(self, df, label, prompt) -> List[str]:
        return df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def filter_prompts_bfs(self, df, label) -> List[str]:
        cluster_distances = self.history_manager.prompts_manager.cluster_distances
        relevant_distances = {pair: dist for pair, dist in cluster_distances.items() if label in pair}

        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                closest_cluster_label = pair.split(',')[0] if pair.split(',')[1] == label else pair.split(',')[1]

        return df[(df['labels'] == closest_cluster_label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def compute_probabilities(self, prompts: List[str]) -> List[float]:
        return [self.history_manager.prompt_probabilities['no_params'].get(prompt, 0) for prompt in prompts]

    def create_params_list(self, size: int) -> List[None]:
        return [None] * size


class ParamRecommendation(MainRecommender):
    def filter_prompts_dfs(self, df, label, prompt) -> List[str]:
        key_param = df[df['prompts'] == prompt]['params'].str[0].iloc[0]
        return df[df['params'].apply(lambda x: str(x) == str([key_param]))]['prompts'].tolist()

    def filter_prompts_bfs(self, df, label) -> List[str]:
        return df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x) == 0))]['prompts'].tolist()

    def compute_probabilities(self, prompts: List[str]) -> List[float]:
        key_param = df[df['prompts'] == self.user_selection.prompt]['params'].str[0].iloc[0]
        key_param_value = self.user_selection.parameters[key_param]
        
        for prompt in prompts:
            if key_param_value not in self.history_manager.prompt_probabilities['params'].get(prompt, {}).get(key_param, {}):
                self.history_manager.prompt_probabilities['params'][prompt][key_param][key_param_value] = 1
        
        return [self.history_manager.prompt_probabilities['params'][prompt][key_param][key_param_value] for prompt in prompts]

    def create_params_list(self, size: int) -> List[Dict[str, Any]]:
        key_param = self.history_manager.prompts_manager.df_prompts[df_prompts['prompts'] == self.user_selection.prompt]['params'].str[0].iloc[0]
        key_param_value = self.user_selection.parameters[key_param]
        return [{key_param: key_param_value}] * size


# Example usage
history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)

print(param_rec.give_recommendation(mode='dfs', size=user_selection_params.numDeepDive))
print(param_rec.give_recommendation(mode='bfs', size=user_selection_params.numExploration))
