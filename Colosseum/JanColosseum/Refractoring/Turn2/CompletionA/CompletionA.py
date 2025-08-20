from typing import List, Dict, Any
import numpy as np

class BaseRecommender(BaseModel):
    user_choice: UserChoice
    history_mgr: HistoryManager

    def recommend(self, mode: str):
        candidate_prompts = self.find_candidate_prompts()
        probs = self.calculate_probabilities(candidate_prompts)
        normalized_probs = self.normalize_probabilities(probs)
        
        if mode == "deep_dive":
            num_recommendations = self.user_choice.numDeepDive
        elif mode == "exploration":
            num_recommendations = self.user_choice.numExploration
        else:
            raise ValueError("Invalid recommendation mode")

        if not candidate_prompts or not normalized_probs:
            return []

        recommended_prompts = np.random.choice(candidate_prompts, size=num_recommendations, replace=False, p=normalized_probs)
        params = self.get_params_for_recommendation(candidate_prompts)
        self.history_mgr.update_prompt_probs(recommended_prompts, params=params, mode='recommendations')
        
        return recommended_prompts

    def normalize_probabilities(self, probs) -> List[float]:
        if not probs:
            print("No probabilities found. Cannot sample.")
            return []
        total_prob = sum(probs)
        if total_prob == 0:
            print("Total probability is zero, cannot sample.")
            return []
        return [prob / total_prob for prob in probs]

    def find_candidate_prompts(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    def calculate_probabilities(self, candidate_prompts):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_params_for_recommendation(self, candidate_prompts) -> List[Any]:
        raise NotImplementedError("This method should be implemented by subclasses")


class NoParamsRecommender(BaseRecommender):
    def find_candidate_prompts(self) -> List[str]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        label = df[df['prompts'] == prompt]['labels'].iloc[0]  # Get the label for the current prompt.
        candidate_prompts = df[(df['labels'] == label) & (df['params'].apply(len) == 0)]['prompts'].tolist()
        return candidate_prompts

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        return [self.history_mgr.prompt_probs['no_params'].get(prompt, 1) for prompt in candidate_prompts]

    def get_params_for_recommendation(self, candidate_prompts: List[str]) -> List[None]:
        return [None] * len(candidate_prompts)


class ParamsRecommender(BaseRecommender):
    def find_candidate_prompts(self) -> List[str]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df[df['prompts'] == prompt]['params'].str[0].iloc[0]  # Get the lead parameter from the prompt.
        candidate_prompts = df[df['params'].apply(lambda x: str(x) == str([lead_param]))]['prompts'].tolist()
        return candidate_prompts

    def calculate_probabilities(self, candidate_prompts: List[str]) -> List[float]:
        prompt = self.user_choice.prompt
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df[df['prompts'] == prompt]['params'].str[0].iloc[0]
        lead_param_value = self.user_choice.parameters[lead_param]

        return [
            self.history_mgr.prompt_probs['params'].get(prompt, {}).get(lead_param, {}).get(lead_param_value, 1)
            for prompt in candidate_prompts
        ]

    def get_params_for_recommendation(self, candidate_prompts: List[str]) -> List[Dict[str, Any]]:
        df = self.history_mgr.prompts_mgr.df_prompts
        lead_param = df[df['prompts'] == self.user_choice.prompt]['params'].str[0].iloc[0]
        lead_param_value = self.user_choice.parameters[lead_param]
        return [{lead_param: lead_param_value} for _ in candidate_prompts]


# Example Usage

history_mgr = HistoryManager(prompts_mgr=prompts_mgr, org_id=ORG_ID, id=ID)
user_choice_params = UserChoice(prompt="example_prompt", numDeepDive=3, numExploration=2, parameters={"param_name": "param_value"})

pr = ParamsRecommender(user_choice=user_choice_params, history_mgr=history_mgr)
print(user_choice_params.prompt)
print(pr.recommend(mode="deep_dive"))
print(pr.recommend(mode="exploration"))
