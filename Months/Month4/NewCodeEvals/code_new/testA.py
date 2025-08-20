import unittest
import numpy as np
from ideal_completion import ExtremelyAdvancedLinearRegression

class TestExtremelyAdvancedLinearRegression(unittest.TestCase):

    def test_fit_predict(self):
        # Test that the model can fit and predict properly on a simple dataset
        np.random.seed(0)
        X = np.random.rand(100, 3)
        y = 4 * X[:, 0] - 2 * X[:, 1] + X[:, 2] + np.random.randn(100) * 0.1

        model = ExtremelyAdvancedLinearRegression(
            learning_rate=0.01,
            n_iterations=500,
            regularization='none',
            optimizer='adam',
            polynomial_degree=1,
            batch_size=None,
            early_stopping=False,
            feature_selection=False
        )
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = model.score(X, y)
        self.assertGreater(r2, 0.95)

    def test_early_stopping(self):
        # Test that early stopping stops training early when validation loss doesn't improve
        np.random.seed(0)
        X_train = np.random.rand(80, 3)
        y_train = 3 * X_train[:, 0] + 2 * X_train[:, 1] + X_train[:, 2] + np.random.randn(80) * 0.1

        X_val = np.random.rand(20, 3)
        y_val = 3 * X_val[:, 0] + 2 * X_val[:, 1] + X_val[:, 2] + np.random.randn(20) * 0.1

        model = ExtremelyAdvancedLinearRegression(
            learning_rate=0.01,
            n_iterations=1000,
            regularization='none',
            optimizer='adam',
            polynomial_degree=1,
            early_stopping=True,
            patience=5,
            feature_selection=False
        )
        model.fit(X_train, y_train, X_val, y_val)
        # Check that the number of iterations is less than n_iterations due to early stopping
        self.assertLess(len(model.training_loss), 1000)

    def test_feature_selection(self):
        # Test that feature selection selects the correct number of features
        np.random.seed(0)
        X = np.random.rand(100, 5)  # 5 features
        y = 2 * X[:, 0] - 3 * X[:, 2] + np.random.randn(100) * 0.1

        model = ExtremelyAdvancedLinearRegression(
            learning_rate=0.01,
            n_iterations=500,
            regularization='none',
            optimizer='adam',
            polynomial_degree=1,
            early_stopping=False,
            feature_selection=True,
            n_features_to_select=2
        )
        model.fit(X, y)
        # Ensure that only 2 features are selected
        self.assertEqual(len(model.selected_features), 2)
        # Check that the selected features include indices 0 and 2
        self.assertIn(0, model.selected_features)
        self.assertIn(2, model.selected_features)

    def test_predict_before_fit(self):
        # Test that predicting before fitting raises an AttributeError
        model = ExtremelyAdvancedLinearRegression()
        X = np.random.rand(10, 3)
        with self.assertRaises(AttributeError):
            model.predict(X)

if __name__ == '__main__':
    unittest.main(verbosity=2)
