
import json
from typing import List, Dict, Callable

# Class for NestedPromptCreator
class NestedPromptCreator:
    def __init__(self, base_prompt: str):
        self.base_prompt = base_prompt
        self.sub_tasks = []

    def add_sub_task(self, task_details: str, task_type: str):
        sub_task = {
            "details": task_details,
            "type": task_type
        }
        self.sub_tasks.append(sub_task)

    def create_prompt(self) -> str:
        prompt_structure = {
            "base_prompt": self.base_prompt,
            "sub_tasks": self.sub_tasks
        }
        return json.dumps(prompt_structure, indent=4)

# Class for IterativePromptFormulator
class IterativePromptFormulator:
    @staticmethod
    def iterate_prompt(initial_prompt: str, cycles: int) -> List[str]:
        prompts = [initial_prompt]
        for i in range(cycles):
            refined_prompt = f"Refinement {i+1}: Enhance the prompt.\n{prompts[-1]}"
            prompts.append(refined_prompt)
        return prompts

# Class for PromptAssessor
class PromptAssessor:
    @staticmethod
    def assess_prompts(prompts: Dict[str, str], 
                       evaluation_functions: Dict[str, Callable[[str], float]]) -> Dict[str, Dict[str, float]]:
        results = {}
        for name, prompt in prompts.items():
            results[name] = {}
            for metric, func in evaluation_functions.items():
                results[name][metric] = func(prompt)
        return results

# Class for TaskFragmentor
class TaskFragmentor:
    @staticmethod
    def fragment_task(task: str, fragment_level: int = 2) -> List[str]:
        if fragment_level == 0:
            return [task]
        
        sub_tasks = [f"Sub-task {i+1} of '{task}'" for i in range(2)]
        fragmented = []
        for sub in sub_tasks:
            fragmented.extend(TaskFragmentor.fragment_task(sub, fragment_level - 1))
        return fragmented

# LogicNode class for LogicTreeConstructor
from dataclasses import dataclass, field

@dataclass
class LogicNode:
    thought: str
    children: List['LogicNode'] = field(default_factory=list)

# Class for LogicTreeConstructor
class LogicTreeConstructor:
    def __init__(self, initial_thought: str):
        self.root = LogicNode(initial_thought)

    def add_thought(self, parent_thought: str, new_thought: str) -> bool:
        parent_node = self._find_thought(self.root, parent_thought)
        if parent_node:
            parent_node.children.append(LogicNode(new_thought))
            return True
        return False

    def _find_thought(self, node: LogicNode, thought: str) -> LogicNode:
        if node.thought == thought:
            return node
        for child in node.children:
            result = self._find_thought(child, thought)
            if result:
                return result
        return None

    def display_tree(self, node: LogicNode = None, level: int = 0):
        if node is None:
            node = self.root
        print("    " * level + f"- {node.thought}")
        for child in node.children:
            self.display_tree(child, level + 1)
