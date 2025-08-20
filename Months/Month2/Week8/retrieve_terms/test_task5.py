import unittest
from task5 import retrieve_terms

class TestRetrieveTerms(unittest.TestCase):

    def test_basic_functionality(self):
        # This test checks if the function can correctly identify and extract
        # both an action word and a multi-word technical term.
        # It's important because it verifies the core functionality of the function.
        question = "[Purpose Question]: Analyze the performance of Machine Learning algorithms in a multi-dimensional space."
        expected = ["Analyze", "Machine Learning"]
        self.assertEqual(set(retrieve_terms(question)), set(expected))

    def test_multiple_technical_terms(self):
        # This test verifies the function's ability to extract multiple multi-word technical terms and an action word.
        # It's crucial to ensure the function works correctly with complex inputs.
        question = "[Purpose Question]: Compare the efficiency of Deep Learning and Reinforcement Learning in Natural Language Processing tasks."
        expected = ["Compare", "Deep Learning", "Reinforcement Learning", "Natural Language Processing"]
        self.assertEqual(set(retrieve_terms(question)), set(expected))

    def test_no_technical_terms(self):
        # This test checks if the function correctly handles a question with only an action word and no technical terms.
        # It's important to ensure the function doesn't falsely identify terms.
        question = "[Purpose Question]: Evaluate the impact of regular exercise on overall health."
        expected = ["Evaluate"]
        self.assertEqual(set(retrieve_terms(question)), set(expected))

    def test_minimal_output(self):
        # This test checks if the function can handle repeated action words and extract terms from word derivatives (e.g., "analytical" from "analysis").
        # It verifies the function's ability to avoid duplicates and identify related terms.
        question = "[Purpose Question]: Analyze and evaluate the analyze analysis of analytical data."
        expected = ["Analyze", "evaluate", "analytical"]
        self.assertEqual(set(retrieve_terms(question)), set(expected))

    def test_maintain_original_phrasing(self):
        # This test ensures that the function maintains the original phrasing of extracted terms, particularly for technical terms that may have unconventional capitalization (e.g., "MachineLearning").
        # It's important for preserving the intended meaning and formatting of terms.
        question = "[Purpose Question]: Implement a MachineLearning algorithm for ImageRecognition."
        expected = ["Implement", "MachineLearning", "ImageRecognition"]
        result = retrieve_terms(question)
        self.assertTrue(all(term in question for term in result))

if __name__ == '__main__':
    unittest.main(verbosity=2)