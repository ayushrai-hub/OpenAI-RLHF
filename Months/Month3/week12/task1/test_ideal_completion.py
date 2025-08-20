import unittest
import json
from io import StringIO
from unittest.mock import patch
from typing import Callable, Dict

from testable_ideal_completion import (
    NestedPromptCreator,
    IterativePromptFormulator,
    PromptAssessor,
    TaskFragmentor,
    LogicTreeConstructor,
    LogicNode
)

class TestNestedPromptCreator(unittest.TestCase):
    def setUp(self):
        self.creator = NestedPromptCreator("Test Base Prompt")

    # This tests if sub-tasks are correctly added to the NestedPromptCreator.
    def test_add_sub_task(self):
        self.creator.add_sub_task("Sub Task 1", "Type 1")
        self.assertEqual(len(self.creator.sub_tasks), 1)
        self.assertEqual(self.creator.sub_tasks[0]["details"], "Sub Task 1")
        self.assertEqual(self.creator.sub_tasks[0]["type"], "Type 1")

    # This verifies that the JSON output is formatted correctly and contains all added sub-tasks.
    def test_create_prompt(self):
        self.creator.add_sub_task("Sub Task 1", "Type 1")
        self.creator.add_sub_task("Sub Task 2", "Type 2")
        prompt = self.creator.create_prompt()
        prompt_dict = json.loads(prompt)
        self.assertEqual(prompt_dict["base_prompt"], "Test Base Prompt")
        self.assertEqual(len(prompt_dict["sub_tasks"]), 2)

class TestIterativePromptFormulator(unittest.TestCase):
    def test_iterate_prompt(self):
        # This test ensures that the iterative refinement process works as intended.
        initial_prompt = "Initial prompt"
        prompts = IterativePromptFormulator.iterate_prompt(initial_prompt, 3)
        self.assertEqual(len(prompts), 4)  # Initial + 3 refinements
        self.assertEqual(prompts[0], initial_prompt)
        for i, prompt in enumerate(prompts[1:], 1):
            self.assertIn(f"Refinement {i}: Enhance the prompt.", prompt)

class TestPromptAssessor(unittest.TestCase):
    # This test verifies that the assessment process works for multiple prompts and metrics.
    def test_assess_prompts(self):
        prompts = {
            "Prompt1": "This is a test prompt.",
            "Prompt2": "This is another test prompt, but longer."
        }
        evaluation_functions = {
            "Length": len,
            "WordCount": lambda p: len(p.split())
        }
        results = PromptAssessor.assess_prompts(prompts, evaluation_functions)
        self.assertEqual(len(results), 2)
        # Test prompt 1
        self.assertEqual(results["Prompt1"]["Length"], len(prompts["Prompt1"]))
        self.assertEqual(results["Prompt1"]["WordCount"], len(prompts["Prompt1"].split()))

        # Test prompt2
        self.assertEqual(results["Prompt2"]["Length"], len(prompts["Prompt2"]))
        self.assertEqual(results["Prompt2"]["WordCount"], len(prompts["Prompt2"].split()))

        # Additional assertions to ensure correct functionality
        self.assertGreater(results["Prompt2"]["Length"], results["Prompt1"]["Length"])
        self.assertGreater(results["Prompt2"]["WordCount"], results["Prompt1"]["WordCount"])

class TestTaskFragmenter(unittest.TestCase):
    def test_fragment_task(self):
        # This test ensures that the fragmentation process works at the specified depth.
        task = "Main Task"
        fragments = TaskFragmentor.fragment_task(task, 2)
        self.assertEqual(len(fragments), 4)
        self.assertTrue(all("Sub-task" in fragment for fragment in fragments))

class TestLogicTreeConstructor(unittest.TestCase):
    def setUp(self):
        self.tree = LogicTreeConstructor("Root Thought")

    def test_add_thought(self):
        # This test verifies that the tree structure is maintained and invalid additions are rejected.
        self.assertTrue(self.tree.add_thought("Root Thought", "Child Thought 1"))
        self.assertTrue(self.tree.add_thought("Root Thought", "Child Thought 2"))
        self.assertTrue(self.tree.add_thought("Child Thought 1", "Grandchild Thought"))
        self.assertFalse(self.tree.add_thought("Non-existent Thought", "Orphan Thought"))

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_tree(self, mock_stdout):
        # This test ensures that the visual representation of the tree is accurate.
        self.tree.add_thought("Root Thought", "Child Thought 1")
        self.tree.add_thought("Root Thought", "Child Thought 2")
        self.tree.add_thought("Child Thought 1", "Grandchild Thought")
        self.tree.display_tree()
        output = mock_stdout.getvalue().strip().split('\n')
        self.assertEqual(len(output), 4)
        self.assertIn("Root Thought", output[0])
        self.assertIn("Child Thought 1", output[1])
        self.assertIn("Grandchild Thought", output[2])
        self.assertIn("Child Thought 2", output[3])

if __name__ == '__main__':
    unittest.main(verbosity=2)