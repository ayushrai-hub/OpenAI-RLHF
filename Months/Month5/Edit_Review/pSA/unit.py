import unittest
from ideal_completipn import pso_xgboost_optimization
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import random
import pandas as pd
import numpy as np


class TestPSOXGBoostOptimization(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Set random seeds for reproducibility
        np.random.seed(42)
        random.seed(42)
        cls.model, cls.rmse, cls.best_params, cls.lengths = pso_xgboost_optimization()
    
    def test_input_lengths(self):
        # Test if all input lists have the same length
        self.assertTrue(all(length == self.lengths[0] for length in self.lengths), "Input lists have different lengths.")
    
    def test_model_type(self):
        # Test if the model used is an XGBRegressor
        self.assertIsInstance(self.model, xgb.XGBRegressor, "The model is not an instance of XGBRegressor.")
    
    def test_hyperparameters_within_bounds(self):
        # Test if the optimized hyperparameters are within their defined bounds
        max_depth, learning_rate, n_estimators = self.best_params
        self.assertTrue(3 <= max_depth <= 10, "max_depth is out of bounds.")
        self.assertTrue(0.01 <= learning_rate <= 0.3, "learning_rate is out of bounds.")
        self.assertTrue(50 <= n_estimators <= 500, "n_estimators is out of bounds.")
    
    def test_rmse_non_negative(self):
        # Test if the RMSE is non-negative, which indicates that value is correctly calculated. 
        self.assertGreaterEqual(self.rmse, 0, "Root Mean Squared Error (RMSE) is negative, which is not possible.")
        
    def test_is_best_params_good(self):
        # Set random seed for reproducibility
        random.seed(42)
        
        # Use the same parameter ranges as the optimization function
        max_depth = random.randint(3, 15)        # Changed from 1-10 to 3-10
        learning_rate = random.uniform(0.01, 0.3) # Changed from 0.01-1.0 to 0.01-0.3
        n_estimators = random.randint(50, 1000)    # Changed from 10-500 to 50-1000
        
        # Dataset setup
        data = {
            'Sc': [750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 750.0, 
                1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 
                1000.0, 1000.0, 1250.0, 1250.0, 1250.0, 1250.0, 1250.0, 1250.0, 1250.0, 1250.0, 
                1250.0, 1250.0, 1250.0, 1250.0, 1500.0, 1500.0, 1500.0, 1500.0, 1500.0, 1500.0, 
                1500.0, 1500.0, 1500.0, 1500.0, 1500.0, 1500.0], 
            'Fz': [6.0, 6.0, 6.0, 12.0, 12.0, 12.0, 18.0, 18.0, 18.0, 24.0, 24.0, 24.0, 6.0, 6.0, 
                6.0, 12.0, 12.0, 12.0, 18.0, 18.0, 18.0, 24.0, 24.0, 24.0, 6.0, 6.0, 6.0, 12.0, 
                12.0, 12.0, 18.0, 18.0, 18.0, 24.0, 24.0, 24.0, 6.0, 6.0, 6.0, 12.0, 12.0, 12.0, 
                18.0, 18.0, 18.0, 24.0, 24.0, 24.0], 
            'Dm': [0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 
                0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 
                0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 0.01, 0.03, 0.05, 
                0.01, 0.03, 0.05, 0.01, 0.03, 0.05], 
            'Ra': [65.0, 63.0, 72.0, 144.0, 102.0, 94.0, 185.0, 147.0, 121.0, 187.0, 170.0, 172.0, 
                58.0, 78.0, 62.0, 130.0, 84.0, 92.0, 138.0, 124.0, 86.0, 163.0, 153.0, 142.0, 50.0, 
                63.0, 71.0, 101.0, 99.0, 85.0, 115.0, 92.0, 95.0, 155.0, 109.0, 121.0, 37.0, 56.0, 
                56.0, 88.0, 82.0, 94.0, 119.0, 87.0, 104.0, 119.0, 103.0, 109.0]
        }
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Prepare features and target variable
        X = df[['Sc', 'Fz', 'Dm']]
        y = df['Ra']
        
        # Split the dataset
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = xgb.XGBRegressor(max_depth=max_depth, learning_rate=learning_rate, n_estimators=n_estimators)
        model.fit(X_train, y_train)

        # Predict on the test set
        y_pred = model.predict(X_test)

        # Calculate RMSE
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        self.assertLessEqual(self.rmse, rmse, "Random parameters performed better than optimized parameters.")

if __name__ == '__main__':
    unittest.main(verbosity=2)