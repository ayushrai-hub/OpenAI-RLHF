from typing import List, Any
import numpy as np

class MainRecommender(BaseModel):
    user_selection: UserSelection
    history_manager: HistoryLogger

    def give_recommendation_dfs(self):
        raise NotImplementedError("Should be implemented by subclass.")

    def give_recommendation_bfs(self):
        raise NotImplementedError("Should be implemented by subclass.")

    def standardize_probabilities(self, probs: List[float]) -> List[float]:
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability is zero; cannot standardize.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history(self, recommended_prompts: List[str], params: List[Any]):
        self.history_manager.update_prompt_probabilities(
            recommended_prompts,
            params=params,
            mode='recommendations'
        )

    def fetch_possible_prompts(self, label, param_filter):
        df = self.history_manager.prompts_manager.df_prompts
        filtered_df = df[(df.labels == label) & param_filter(df)]
        return filtered_df['prompts'].tolist()


class NoParamsRecommendation(MainRecommender):

    def give_recommendation_dfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]
        possible_prompts = self.fetch_possible_prompts(
            label,
            lambda df: df['params'].apply(lambda x: len(x) == 0)
        )
        
        probs = [self.history_manager.prompt_probabilities['no_params'].get(p, 1) for p in possible_prompts]
        normalized_probs = self.standardize_probabilities(probs)
        
        recommended_prompts = np.random.choice(
            possible_prompts,
            size=self.user_selection.numDeepDive,
            replace=False,
            p=normalized_probs
        ).tolist()

        self.update_history(recommended_prompts, [None] * self.user_selection.numDeepDive)

        return recommended_prompts

    def give_recommendation_bfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]

        # Find closest cluster
        relevant_distances = {
            pair: dist for pair, dist in self.history_manager.prompts_manager.cluster_distances.items() 
            if label in pair
        }
        closest_pair = min(relevant_distances, key=relevant_distances.get)
        closest_label = closest_pair.replace(label, "").replace(",", "").strip()

        possible_prompts = self.fetch_possible_prompts(
            closest_label,
            lambda df: df['params'].apply(lambda x: len(x) == 0)
        )

        probs = [self.history_manager.prompt_probabilities['no_params'].get(p, 1) for p in possible_prompts]
        normalized_probs = self.standardize_probabilities(probs)

        recommended_prompts = np.random.choice(
            possible_prompts,
            size=self.user_selection.numExploration,
            replace=False,
            p=normalized_probs
        ).tolist()

        self.update_history(recommended_prompts, [None] * self.user_selection.numExploration)

        return recommended_prompts


class ParamRecommendation(MainRecommender):

    def give_recommendation_dfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts

        key_param = df.loc[df['prompts'] == prompt, 'params'].iloc[0][0]
        key_param_value = self.user_selection.parameters[key_param]

        possible_prompts = self.fetch_possible_prompts(
            label=df.loc[df['prompts'] == prompt, 'labels'].iloc[0],
            param_filter=lambda df: df['params'].apply(lambda x: x == [key_param])
        )

        # Ensure probabilities exist for the parameter value
        for p in possible_prompts:
            params_probs = self.history_manager.prompt_probabilities['params']
            if p not in params_probs:
                params_probs[p] = {}
            if key_param not in params_probs[p]:
                params_probs[p][key_param] = {}
            if key_param_value not in params_probs[p][key_param]:
                params_probs[p][key_param][key_param_value] = 1

        probs = [
            self.history_manager.prompt_probabilities['params'][p][key_param][key_param_value]
            for p in possible_prompts
        ]

        normalized_probs = self.standardize_probabilities(probs)

        recommended_prompts = np.random.choice(
            possible_prompts,
            size=self.user_selection.numDeepDive,
            replace=False,
            p=normalized_probs
        ).tolist()

        self.update_history(recommended_prompts, [{key_param: key_param_value}] * self.user_selection.numDeepDive)

        return recommended_prompts

    def give_recommendation_bfs(self):
        prompt = self.user_selection.prompt
        df = self.history_manager.prompts_manager.df_prompts
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]

        possible_prompts = self.fetch_possible_prompts(
            label,
            lambda df: df['params'].apply(lambda x: len(x) == 0)
        )

        probs = [self.history_manager.prompt_probabilities['no_params'].get(p, 1) for p in possible_prompts]
        normalized_probs = self.standardize_probabilities(probs)

        recommended_prompts = np.random.choice(
            possible_prompts,
            size=self.user_selection.numExploration,
            replace=False,
            p=normalized_probs
        ).tolist()

        self.update_history(recommended_prompts, [None] * self.user_selection.numExploration)

        return recommended_prompts

# Usage example:
history_manager = HistoryLogger(prompts_manager=prompts_manager, org_id=ORG_ID, id=ID)
param_rec = ParamRecommendation(user_selection=user_selection_params, history_manager=history_manager)

print(user_selection_params.prompt)
print(param_rec.give_recommendation_dfs())
print(param_rec.give_recommendation_bfs())
