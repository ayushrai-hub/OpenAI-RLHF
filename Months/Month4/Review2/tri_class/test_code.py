import unittest
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import pandas as pd
from testable_code import EvaluateModel, classify_duration, tri_class_ranges

class TestEvaluateModel(unittest.TestCase):
    def setUp(self):
        # Setting up mock data for testing
        self.actual_categorized = ['0-8h', '8-40h', '40+h', '0-8h']
        self.predicted_categorized = ['0-8h', '40+h', '40+h', '8-40h']
        self.labels = list(tri_class_ranges.keys())
        
        # Expected confusion matrix based on above labels
        self.expected_confusion_matrix = np.array([
            [1, 1, 0],
            [0, 0, 1],
            [0, 0, 1]
        ])
        
        self.evaluator = EvaluateModel(
            actual_categorization=self.actual_categorized,
            predicted_categorization=self.predicted_categorized,
            labels=self.labels
        )

    def test_run_evaluation_classification_report(self):
        # Test to check if classification report contains expected keys
        cls_report, _ = self.evaluator.run_evaluation()
        for label in self.labels:
            self.assertIn(label, cls_report)
        # Check an individual metric in the report
        self.assertIn('precision', cls_report['0-8h'])

    def test_run_evaluation_confusion_matrix(self):
        # Test to verify confusion matrix values
        _, confusion_mat = self.evaluator.run_evaluation()
        np.testing.assert_array_equal(confusion_mat, self.expected_confusion_matrix)

    def test_classify_duration(self):
        # Test the classify_duration function with various durations
        self.assertEqual(classify_duration(100), '0-8h')
        self.assertEqual(classify_duration(1000), '8-40h')
        self.assertEqual(classify_duration(3000), '40+h')

if __name__ == '__main__':
    unittest.main(verbosity=2)