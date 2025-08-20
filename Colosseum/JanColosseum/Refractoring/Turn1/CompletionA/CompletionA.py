class BaseRecommender(BaseModel):
    """
    Base class for recommender systems.
    """
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend_dfs(self):
        """
        Method to recommend based on depth-first search.
        To be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def recommend_bfs(self):
        """
        Method to recommend based on breadth-first search.
        To be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def normalize_probabilities(self, probs) -> List[float]:
        """
        Normalize probabilities to ensure they sum up to 1.
        
        Args:
        - probs (List[float]): List of probabilities to normalize.
        
        Returns:
        - List[float]: Normalized probabilities.
        """
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability for the cluster is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

class NoParamsRecommender(BaseRecommender):
    """
    Recommender for scenarios where no parameters are provided.
    """
    def recommend_dfs(self):
        """
        Recommends based on depth-first search without parameters.
        """
        return self.recommend_generic('dfs')

    def recommend_bfs(self):
        """
        Recommends based on breadth-first search without parameters.
        """
        return self.recommend_generic('bfs')

    def recommend_generic(self, mode: str):
        """
        Generic recommendation method.

        Args:
        - mode (str): Mode of recommendation ('dfs' or 'bfs').

        Returns:
        - List[str]: List of recommended prompts.
        """
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df.loc[df['prompts'] == prompt, 'labels'].iloc[0]

        if mode == 'dfs':
            num_recommendations = self.user_choice.numDeepDive
        elif mode == 'bfs':
            # Finding the closest cluster label for bfs
            relevant_distances = {pair: dist for pair, dist in self.history_mgr.prompts_mgr.cluster_distances.items() if label in pair}
            min_distance = min(relevant_distances.values())
            closest_cluster_label = [pair.replace(label, '').replace(',', '') for pair, dist in relevant_distances.items() if dist == min_distance][0]
            label = closest_cluster_label
            num_recommendations = self.user_choice.numExploration

        candidate_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x)==0))]['prompts'].tolist()
        probs = [self.history_mgr.prompt_probs['no_params'][prompt] for prompt in candidate_prompts]
        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(candidate_prompts, size=num_recommendations, replace=False, p=normalized_probs)
        self.history_mgr.update_prompt_probs(recommended_prompts, params=[None]*num_recommendations, mode='recommendations')

        return recommended_prompts

class ParamsRecommender(BaseRecommender):
    """
    Recommender for scenarios where parameters are provided.
    """
    def recommend_generic(self, lead_param=None, label=None):
        """
        Generic recommendation method.

        Args:
        - lead_param: Lead parameter for recommendation.
        - label: Label for recommendation.

        Returns:
        - List[str]: List of recommended prompts.
        """
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts

        if lead_param is not None:
            candidate_prompts = df[df['params'].apply(lambda x: str(x) == str([lead_param]))]['prompts'].tolist()
            lead_param_value = self.user_choice.parameters[lead_param]
            for prompt in candidate_prompts:
                if lead_param_value not in self.history_mgr.prompt_probs['params'][prompt][lead_param]:
                    self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value] = 1
            probs = [self.history_mgr.prompt_probs['params'][prompt][lead_param][lead_param_value] for prompt in candidate_prompts]
        elif label is not None:
            candidate_prompts = df[(df['labels'] == label) & (df['params'].apply(lambda x: len(x)) == 0)]['prompts'].tolist()
            probs = [self.history_mgr.prompt_probs['no_params'][prompt] for prompt in candidate_prompts]
        else:
            raise ValueError("Either lead_param or label must be provided.")

        normalized_probs = self.normalize_probabilities(probs)
        recommended_prompts = np.random.choice(candidate_prompts, size=self.user_choice.numDeepDive if lead_param else self.user_choice.numExploration, replace=False, p=normalized_probs)
        params = [{lead_param: lead_param_value}] * self.user_choice.numDeepDive if lead_param else [None] * self.user_choice.numExploration
        mode = 'recommendations'
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode=mode)

        return recommended_prompts

    def recommend_dfs(self):
        """
        Recommends based on a depth-first search with parameters.
        """
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df.loc[df['prompts'] == self.user_choice.prompt, 'params'].str[0].iloc[0]
        return self.recommend_generic(lead_param=lead_param)

    def recommend_bfs(self):
        """
        Recommends based on a breadth-first search with labels.
        """
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df.loc[df_prompts['prompts'] == self.user_choice.prompt, 'labels'].iloc[0]
        return self.recommend_generic(label=label)


# Example usage
history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend_dfs())
print(pr.recommend_bfs())
