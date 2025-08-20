#ideal_completion.py

import json
import logging
from typing import List, Dict, Callable
from dataclasses import dataclass, field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LogicNode:
    thought: str
    children: List['LogicNode'] = field(default_factory=list)

class NestedPromptCreator:
    def __init__(self, base_prompt: str):
        self.base_prompt = base_prompt
        self.sub_tasks = []

    def add_sub_task(self, task_details: str, task_type: str):
        """Add a sub-task to the nested prompt structure."""
        try:
            sub_task = {"details": task_details, "type": task_type}
            self.sub_tasks.append(sub_task)
            logger.info(f"Added sub-task: {task_details}")
        except Exception as e:
            logger.error(f"Error adding sub-task: {str(e)}")

    def create_prompt(self) -> str:
        """Generate a JSON representation of the nested prompt."""
        try:
            prompt_structure = {
                "base_prompt": self.base_prompt,
                "sub_tasks": self.sub_tasks
            }
            return json.dumps(prompt_structure, indent=4)
        except Exception as e:
            logger.error(f"Error creating nested prompt: {str(e)}")
            return ""

class IterativePromptFormulator:
    @staticmethod
    def iterate_prompt(initial_prompt: str, cycles: int) -> List[str]:
        """Generate iteratively refined prompts."""
        prompts = [initial_prompt]
        try:
            for i in range(cycles):
                refined_prompt = f"Refinement {i+1}: Enhance the prompt.\n{prompts[-1]}"
                prompts.append(refined_prompt)
            return prompts
        except Exception as e:
            logger.error(f"Error in iterative prompting: {str(e)}")
            return prompts

class PromptAssessor:
    @staticmethod
    def assess_prompts(prompts: Dict[str, str], 
                       evaluation_functions: Dict[str, Callable[[str], float]]) -> Dict[str, Dict[str, float]]:
        """Evaluate prompts using specified metrics."""
        results = {}
        try:
            for name, prompt in prompts.items():
                results[name] = {metric: func(prompt) for metric, func in evaluation_functions.items()}
            return results
        except Exception as e:
            logger.error(f"Error in prompt assessment: {str(e)}")
            return results

class TaskFragmentor:
    @staticmethod
    def fragment_task(task: str, fragment_level: int = 2) -> List[str]:
        """Break down a task into smaller sub-tasks."""
        def _fragment(t: str, level: int) -> List[str]:
            if level == 0:
                return [t]
            sub_tasks = [f"Sub-task {i+1} of '{t}'" for i in range(2)]
            return [item for st in sub_tasks for item in _fragment(st, level - 1)]
        
        try:
            return _fragment(task, fragment_level)
        except Exception as e:
            logger.error(f"Error in task fragmentation: {str(e)}")
            return [task]

class LogicTreeConstructor:
    def __init__(self, initial_thought: str):
        self.root = LogicNode(initial_thought)
        self.last_error = None

    def add_thought(self, parent_thought: str, new_thought: str) -> bool:
        """Add a new thought to the logic tree."""
        def _find_and_add(node: LogicNode, parent: str, new: str) -> bool:
            if node.thought == parent:
                node.children.append(LogicNode(new))
                return True
            return any(_find_and_add(child, parent, new) for child in node.children)

        success = _find_and_add(self.root, parent_thought, new_thought)
        if not success:
            self.last_error = f"Could not add '{new_thought}' to logic tree: Parent thought '{parent_thought}' not found"
        else:
            self.last_error = None
        return success

    def get_last_error(self) -> str:
        """Retrieve the last error message."""
        return self.last_error

    def display_tree(self):
        """Visualize the logic tree structure."""
        def _display(node: LogicNode, level: int = 0):
            print("    " * level + f"- {node.thought}")
            for child in node.children:
                _display(child, level + 1)
        
        _display(self.root)
    
# Example usage
if __name__ == "__main__":
    # Initialize components
    nested_creator = NestedPromptCreator("Develop an AI-driven research assistant")
    logic_tree = LogicTreeConstructor("Develop an AI-driven research assistant")

    # Fragment the main task
    fragments = TaskFragmentor.fragment_task(nested_creator.base_prompt, 2)
    for fragment in fragments:
        nested_creator.add_sub_task(fragment, "Fragmentation")
        logic_tree.add_thought(nested_creator.base_prompt, fragment)

    # Create and iterate the nested prompt
    nested_prompt = nested_creator.create_prompt()
    iterated_prompts = IterativePromptFormulator.iterate_prompt(nested_prompt, 2)

    # Assess the prompts
    assessment_results = PromptAssessor.assess_prompts(
        {"Original": nested_prompt, "Iteration1": iterated_prompts[1]},
        {"Length": len, "Complexity": lambda p: len(p.split()) / len(p)}
    )

    # Display results
    print("Nested Prompt:")
    print(nested_prompt)
    print("\nIterated Prompts:")
    for prompt in iterated_prompts:
        print(prompt)
        print("---")
    print("\nPrompt Assessment:")
    print(json.dumps(assessment_results, indent=2))
    print("\nLogic Tree:")
    logic_tree.display_tree()