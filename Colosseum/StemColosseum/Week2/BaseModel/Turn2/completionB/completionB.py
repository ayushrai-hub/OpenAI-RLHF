from typing import List, Dict, Any

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend(self, candidate_prompts, num_recommendations, params_list, mode, probs):
        normalized_probs = self.normalize_probabilities(probs)
        if not normalized_probs:
            return []
        recommended_prompts = np.random.choice(
            candidate_prompts,
            size=num_recommendations,
            replace=False,
            p=normalized_probs
        )
        self.update_history_manager(recommended_prompts, params_list, mode)
        return recommended_prompts

    def normalize_probabilities(self, probs) -> List[float]:
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def update_history_manager(self, recommended_prompts, params_list, mode):
        self.history_mgr.update_prompt_probs(
            recommended_prompts,
            params=params_list,
            mode=mode
        )

    def recommend_dfs(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def recommend_bfs(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

class NoParamsRecommender(BaseRecommender):

    def recommend_dfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Get the label of the current prompt
        label = df[df['prompts'] == prompt]['labels'].iloc[0]
        
        # Find candidate prompts with the same label and no parameters
        candidate_prompts = df[
            (df['labels'] == label) &
            (df['params'].apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]

        # Prepare the parameters list (None for no parameters)
        params_list = [None] * self.user_choice.numDeepDive

        # Return the recommendations using the shared method
        return self.recommend(
            candidate_prompts,
            self.user_choice.numDeepDive,
            params_list,
            mode='recommendations',
            probs=probs
        )

    def recommend_bfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Get the label of the current prompt
        label = df[df['prompts'] == prompt]['labels'].iloc[0]

        # Find the closest cluster label
        cluster_distances = self.history_mgr.prompts_mgr.cluster_distances
        relevant_distances = {
            pair: dist for pair, dist in cluster_distances.items() if label in pair
        }

        min_distance = float('inf')
        closest_cluster_label = None
        for pair, dist in relevant_distances.items():
            if dist < min_distance:
                min_distance = dist
                labels = pair.split(',')
                closest_label = labels[0] if labels[1] == label else labels[1]
                closest_cluster_label = closest_label

        # Find candidate prompts from the closest cluster with no parameters
        candidate_prompts = df[
            (df['labels'] == closest_cluster_label) &
            (df['params'].apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]

        # Prepare the parameters list (None for no parameters)
        params_list = [None] * self.user_choice.numExploration

        # Return the recommendations using the shared method
        return self.recommend(
            candidate_prompts,
            self.user_choice.numExploration,
            params_list,
            mode='recommendations',
            probs=probs
        )

class ParamsRecommender(BaseRecommender):

    def recommend_dfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Get the lead parameter of the prompt (assuming params is a list)
        lead_param = df[df['prompts'] == prompt]['params'].iloc[0][0]

        # Get the value of the lead parameter from user_choice
        lead_param_value = self.user_choice.parameters[lead_param]

        # Find candidate prompts that have only the lead parameter
        candidate_prompts = df[
            df['params'].apply(lambda x: x == [lead_param])
        ]['prompts'].tolist()

        # Ensure prompt probabilities are initialized
        for p in candidate_prompts:
            if p not in self.history_mgr.prompt_probs['params']:
                self.history_mgr.prompt_probs['params'][p] = {}
            if lead_param not in self.history_mgr.prompt_probs['params'][p]:
                self.history_mgr.prompt_probs['params'][p][lead_param] = {}
            if lead_param_value not in self.history_mgr.prompt_probs['params'][p][lead_param]:
                self.history_mgr.prompt_probs['params'][p][lead_param][lead_param_value] = 1

        # Calculate probabilities for candidate prompts
        probs = [
            self.history_mgr.prompt_probs['params'][p][lead_param][lead_param_value]
            for p in candidate_prompts
        ]

        # Prepare the parameters list
        params_list = [{lead_param: lead_param_value} for _ in range(self.user_choice.numDeepDive)]

        # Return the recommendations using the shared method
        return self.recommend(
            candidate_prompts,
            self.user_choice.numDeepDive,
            params_list,
            mode='recommendations',
            probs=probs
        )

    def recommend_bfs(self):
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        # Get the label of the current prompt
        label = df[df['prompts'] == prompt]['labels'].iloc[0]

        # Find candidate prompts with the same label and no parameters
        candidate_prompts = df[
            (df['labels'] == label) &
            (df['params'].apply(lambda x: len(x) == 0))
        ]['prompts'].tolist()

        # Calculate probabilities for candidate prompts
        probs = [self.history_mgr.prompt_probs['no_params'][p] for p in candidate_prompts]

        # Prepare the parameters list (None for no parameters)
        params_list = [None] * self.user_choice.numExploration

        # Return the recommendations using the shared method
        return self.recommend(
            candidate_prompts,
            self.user_choice.numExploration,
            params_list,
            mode='recommendations',
            probs=probs
        )

# Usage Example
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)

pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend_dfs())
print(pr.recommend_bfs())
