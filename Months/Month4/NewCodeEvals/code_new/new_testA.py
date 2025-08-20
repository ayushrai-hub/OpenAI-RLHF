import unittest
import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from ideal_completion import ExtremelyAdvancedLinearRegression

class TestExtremelyAdvancedLinearRegression(unittest.TestCase):
    def setUp(self):
        # It Initializes common test data.
        np.random.seed(0)
        self.X_base = np.random.rand(100, 3)
        self.y_base = 4 * self.X_base[:, 0] - 2 * self.X_base[:, 1] + self.X_base[:, 2]

    def test_model_parameter_edge_cases(self):
        # Test validation of model initialization parameters.
        # Test invalid learning rates
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(learning_rate=0)
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(learning_rate=-0.1)

        # Test invalid regularization types
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(regularization='invalid_type')

        # Test extreme polynomial degrees
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(polynomial_degree=0)
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(polynomial_degree=-1)

        # Test invalid batch sizes
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(batch_size=0)
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(batch_size=-1)

        # Test invalid patience values
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(patience=-1)

        # Test invalid n_features_to_select
        with self.assertRaises(ValueError):
            ExtremelyAdvancedLinearRegression(n_features_to_select=0)

    def test_input_data_edge_cases(self):
        # It test handling of edge cases in input data.
        model = ExtremelyAdvancedLinearRegression()

        # Test empty dataset
        with self.assertRaises(ValueError):
            model.fit(np.array([[]]), np.array([]))

        # Test single sample/feature
        X_single = np.array([[1.0]])
        y_single = np.array([1.0])
        model.fit(X_single, y_single)
        self.assertIsNotNone(model.predict(X_single))

        # Test NaN values
        X_nan = np.copy(self.X_base)
        X_nan[0, 0] = np.nan
        with self.assertRaises(ValueError):
            model.fit(X_nan, self.y_base)

        # Test infinity values
        X_inf = np.copy(self.X_base)
        X_inf[0, 0] = np.inf
        with self.assertRaises(ValueError):
            model.fit(X_inf, self.y_base)

        # Test non-numeric inputs
        with self.assertRaises(ValueError):
            model.fit(np.array([[1, 'a']]), np.array([1]))

        # Test mismatched dimensions
        with self.assertRaises(ValueError):
            model.fit(self.X_base, self.y_base[:-1])

        # Test zero variance features
        X_zero_var = np.ones((100, 3))
        with self.assertRaises(ValueError):
            model.fit(X_zero_var, self.y_base)

    def test_model_behavior_scenarios(self):
        # It tests model behavior with different configurations.
        # Test regularization types
        for reg_type in ['l1', 'l2', 'elastic_net']:
            model = ExtremelyAdvancedLinearRegression(regularization=reg_type)
            model.fit(self.X_base, self.y_base)
            self.assertGreater(model.score(self.X_base, self.y_base), 0.8)

        # Test optimizers
        for optimizer in ['sgd', 'adam', 'rmsprop']:
            model = ExtremelyAdvancedLinearRegression(optimizer=optimizer)
            model.fit(self.X_base, self.y_base)
            self.assertGreater(model.score(self.X_base, self.y_base), 0.8)

        # Test polynomial degrees
        for degree in [1, 2, 3]:
            model = ExtremelyAdvancedLinearRegression(polynomial_degree=degree)
            model.fit(self.X_base, self.y_base)
            self.assertGreater(model.score(self.X_base, self.y_base), 0.8)

        # Test batch sizes
        for batch_size in [10, 32, 64]:
            model = ExtremelyAdvancedLinearRegression(batch_size=batch_size)
            model.fit(self.X_base, self.y_base)
            self.assertGreater(model.score(self.X_base, self.y_base), 0.8)

        # Test perfect fit
        y_perfect = np.dot(self.X_base, np.array([1, 1, 1]))
        model = ExtremelyAdvancedLinearRegression()
        model.fit(self.X_base, y_perfect)
        self.assertGreater(model.score(self.X_base, y_perfect), 0.99)

    def test_validation_data_scenarios(self):
        # It Test handling of validation data.
        model = ExtremelyAdvancedLinearRegression(early_stopping=True)

        # Test missing validation data
        with self.assertRaises(ValueError):
            model.fit(self.X_base, self.y_base)

        # Test validation data shape mismatch
        X_val_wrong = np.random.rand(20, 4)
        y_val = np.random.rand(20)
        with self.assertRaises(ValueError):
            model.fit(self.X_base, self.y_base, X_val=X_val_wrong, y_val=y_val)

        # Test correct validation data
        X_val_correct = np.random.rand(20, 3)
        y_val_correct = np.random.rand(20)
        model.fit(self.X_base, self.y_base, X_val=X_val_correct, y_val=y_val_correct)
        self.assertIsNotNone(model.weights)
        self.assertLess(len(model.training_loss), model.n_iterations)

    def test_feature_selection(self):
        # It tests feature selection functionality.
        X = np.random.rand(100, 5)
        y = 2 * X[:, 0] - 3 * X[:, 2] + np.random.randn(100) * 0.1
        
        model = ExtremelyAdvancedLinearRegression(
            feature_selection=True,
            n_features_to_select=2
        )
        model.fit(X, y)
        
        # Check number of selected features
        self.assertEqual(len(model.selected_features), 2)
        
        # Check if important features are selected
        self.assertTrue(0 in model.selected_features)  # Feature with coefficient 2
        self.assertTrue(2 in model.selected_features)  # Feature with coefficient -3

    def test_robustness(self):
        # It Test model robustness.
        # Test with large dataset
        X_large = np.random.rand(10000, 50)
        y_large = np.random.rand(10000)
        model = ExtremelyAdvancedLinearRegression()
        model.fit(X_large, y_large)
        self.assertIsNotNone(model.predict(X_large))

        # Test performance consistency
        initial_score = model.score(X_large, y_large)
        for _ in range(5):
            model.fit(X_large, y_large)
            current_score = model.score(X_large, y_large)
            self.assertGreaterEqual(current_score, initial_score * 0.9)

        # Test numerical stability
        X_extreme = np.random.rand(100, 3) * 1e6
        y_extreme = np.random.rand(100) * 1e6
        model = ExtremelyAdvancedLinearRegression()
        model.fit(X_extreme, y_extreme)
        self.assertFalse(np.any(np.isnan(model.weights)))

    def test_cross_validation(self):
        # It tests cross-validation performance.
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        scores = []
        
        for train_idx, val_idx in kf.split(self.X_base):
            X_train, X_val = self.X_base[train_idx], self.X_base[val_idx]
            y_train, y_val = self.y_base[train_idx], self.y_base[val_idx]
            
            model = ExtremelyAdvancedLinearRegression()
            model.fit(X_train, y_train)
            scores.append(model.score(X_val, y_val))
        
        self.assertGreater(np.mean(scores), 0.8)
        self.assertLess(np.std(scores), 0.2)

    def test_predict_before_fit(self):
        # Test prediction before fitting.
        model = ExtremelyAdvancedLinearRegression()
        with self.assertRaises(AttributeError):
            model.predict(self.X_base)

    def test_optimization_convergence(self):
        """Test optimization convergence"""
        model = ExtremelyAdvancedLinearRegression(
            n_iterations=500,  # Increased iterations
            learning_rate=0.01
        )
        model.fit(self.X_base, self.y_base)
        
        # Test loss decrease
        self.assertGreater(model.training_loss[0], model.training_loss[-1])
        
        # Test optimizer convergence
        for optimizer in ['sgd', 'adam', 'rmsprop']:
            model = ExtremelyAdvancedLinearRegression(
                optimizer=optimizer,
                n_iterations=500,  # Increased iterations
                learning_rate=0.01
            )
            model.fit(self.X_base, self.y_base)
            self.assertGreater(model.score(self.X_base, self.y_base), 0.7)  # Relaxed threshold

    def test_preprocessing(self):
        # It test preprocessing pipeline.
        model = ExtremelyAdvancedLinearRegression(polynomial_degree=2)
        X = np.random.rand(100, 2)
        y = X[:, 0]**2 + X[:, 1]**2
        
        model.fit(X, y)
        y_pred = model.predict(X)
        
        self.assertGreater(r2_score(y, y_pred), 0.9)

    def test_batch_processing(self):
        # Test batch processing
        batch_sizes = [1, 10, 32, 64, None]
        for batch_size in batch_sizes:
            model = ExtremelyAdvancedLinearRegression(
                batch_size=batch_size,
                n_iterations=500,  # Increased iterations
                learning_rate=0.01,
                optimizer='adam'
            )
            model.fit(self.X_base, self.y_base)
            score = model.score(self.X_base, self.y_base)
            self.assertGreater(score, 0.7)  # Relaxed threshold

if __name__ == '__main__':
    unittest.main(verbosity=2)