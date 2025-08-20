import unittest
import numpy as np
from ideal_completion import SimpleDecisionTree, SimpleLogisticRegression

class TestSimpleDecisionTree(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = np.array([[0], [1], [2], [3], [4], [5]])
        self.y = np.array([0, 0, 0, 1, 1, 1])
        self.model = SimpleDecisionTree(max_depth=2)

    def test_decision_tree_correct_prediction(self):
        # Verifies that the decision tree makes accurate predictions on training data
        # This ensures the model can properly memorize data within its depth constraint
        self.model.fit(self.X, self.y)
        predictions = self.model.predict(self.X)
        np.testing.assert_array_equal(predictions, self.y)

    def test_decision_tree_single_class(self):
        # Tests the tree's behavior when all labels belong to the same class
        # This ensures the tree defaults to a single leaf node with the correct class
        X = np.array([[0], [1], [2]])
        y = np.array([1, 1, 1])
        model = SimpleDecisionTree(max_depth=1)
        model.fit(X, y)
        predictions = model.predict(X)
        np.testing.assert_array_equal(predictions, y)

    def test_decision_tree_unseen_data(self):
        # Verifies the model's ability to predict for unseen data based on learned splits
        # This ensures that the tree generalizes its learned structure
        self.model.fit(self.X, self.y)
        X_new = np.array([[1.5], [3.5], [7]])
        predictions = self.model.predict(X_new)
        expected = np.array([0, 1, 1])
        np.testing.assert_array_equal(predictions, expected)

    def test_decision_tree_zero_depth(self):
        # Tests the tree's behavior when max depth is zero
        # Ensures that the model defaults to predicting the majority class
        model = SimpleDecisionTree(max_depth=0)
        model.fit(self.X, self.y)
        predictions = model.predict(self.X)
        expected = np.array([1] * len(self.y)) if np.sum(self.y) > len(self.y) / 2 else np.array([0] * len(self.y))
        np.testing.assert_array_equal(predictions, expected)

    def test_decision_tree_boundary_conditions(self):
        # Tests behavior when all features have the same value
        # Ensures the tree defaults to predicting the majority class
        X = np.array([[1], [1], [1]])
        y = np.array([0, 1, 1])
        model = SimpleDecisionTree(max_depth=1)
        model.fit(X, y)
        predictions = model.predict(X)
        expected = np.array([1, 1, 1])
        np.testing.assert_array_equal(predictions, expected)

class TestSimpleLogisticRegression(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = np.array([[1], [2], [3], [4], [5], [6]])
        self.y = np.array([0, 0, 0, 1, 1, 1])
        self.model = SimpleLogisticRegression(lr=0.1, n_iter=1000)

    def test_logistic_regression_edge_case(self):
        # Verifies the model's behavior on non-linearly separable data
        # Ensures the model outputs valid binary predictions
        X = np.array([[0], [1], [2], [3]])
        y = np.array([0, 1, 0, 1])
        model = SimpleLogisticRegression(lr=0.1, n_iter=1000)
        model.fit(X, y)
        predictions = model.predict(X)
        self.assertTrue(np.all(np.isin(predictions, [0, 1])))

    def test_logistic_regression_constant_features(self):
        # Tests behavior when all features are constant
        # Ensures predictions converge to the majority class
        X = np.array([[1], [1], [1]])
        y = np.array([0, 1, 1])
        model = SimpleLogisticRegression(lr=0.1, n_iter=100)
        model.fit(X, y)
        predictions = model.predict(X)
        expected = np.array([1, 1, 1])
        np.testing.assert_array_equal(predictions, expected)

    def test_logistic_regression_correct_prediction(self):
        # Verifies that the logistic regression model makes correct predictions on linearly separable data
        # Ensures that the model's gradient descent converges to an optimal solution
        self.model.fit(self.X, self.y)
        predictions = self.model.predict(self.X)
        np.testing.assert_array_equal(predictions, self.y)

    def test_logistic_regression_large_dataset(self):
        # Tests the model's performance on a larger dataset
        # Ensures that it achieves high accuracy on linearly separable data with sufficient iterations
        np.random.seed(0)
        X = np.random.rand(1000, 5)
        y = (np.sum(X, axis=1) > 2.5).astype(int)
        model = SimpleLogisticRegression(lr=0.001, n_iter=10000)
        model.fit(X, y)
        predictions = model.predict(X)
        accuracy = np.mean(predictions == y)
        self.assertGreaterEqual(accuracy, 0.95)
    
    def test_logistic_regression_zero_iterations(self):
        # Verifies that predictions default to zeros when no training iterations are performed
        # Ensures proper initialization and handling of untrained models
        model = SimpleLogisticRegression(lr=0.1, n_iter=0)
        model.fit(self.X, self.y)
        predictions = model.predict(self.X)
        expected = np.zeros_like(self.y)
        np.testing.assert_array_equal(predictions, expected)

if __name__ == "__main__":
    unittest.main(verbosity=2)