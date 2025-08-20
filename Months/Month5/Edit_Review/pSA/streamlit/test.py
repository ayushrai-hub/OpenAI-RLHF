#ideal_completion.py

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
import pyswarms as ps

def pso_xgboost_optimization() -> Tuple[xgb.XGBRegressor, float, Tuple[int, float, int], Tuple[int, int, int, int]]:
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
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

    # Define the objective function for PSO
    def objective_function(params: np.ndarray) -> np.ndarray:
        n_particles = params.shape[0]
        scores = []

        for i in range(n_particles):
            max_depth = int(params[i, 0])
            learning_rate = params[i, 1]
            n_estimators = int(params[i, 2])

            # Adjusted bounds for better performance
            max_depth = max(3, min(max_depth, 15))  # Changed from 1-10 to 3-15
            learning_rate = max(0.01, min(learning_rate, 0.3))  # Changed upper bound to 0.3
            n_estimators = max(50, min(n_estimators, 1000))  # Changed from 10-500 to 50-1000

            model = xgb.XGBRegressor(
                max_depth=max_depth,
                learning_rate=learning_rate,
                n_estimators=n_estimators,
                min_child_weight=1,
                gamma=0,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0,
                reg_lambda=1
            )

            # Use 5-fold CV instead of 3-fold for better validation
            score = -cross_val_score(model, X_train, y_train, cv=5, scoring='neg_root_mean_squared_error').mean()
            scores.append(score)

        return np.array(scores)

    # Adjusted PSO parameters for faster optimization
    options = {
        'c1': 0.9,    # Increased cognitive parameter for faster convergence
        'c2': 0.7,    # Increased social parameter
        'w': 0.6,     # Reduced inertia for faster convergence
    }
    dimensions = 3
    bounds = (np.array([3, 0.01, 50]), np.array([10, 0.3, 500]))  # Reduced upper bounds

    # Reduced number of particles and iterations for faster execution
    optimizer = ps.single.GlobalBestPSO(
        n_particles=8,  # Reduced from 20
        dimensions=dimensions,
        options=options,
        bounds=bounds,
    )

    # Perform optimization with fewer iterations
    cost, pos = optimizer.optimize(objective_function, iters=10)

    # Extract the best hyperparameters
    best_max_depth = int(pos[0])
    best_learning_rate = pos[1]
    best_n_estimators = int(pos[2])

    # Train the final model using the best hyperparameters
    best_model = xgb.XGBRegressor(max_depth=best_max_depth, learning_rate=best_learning_rate, n_estimators=best_n_estimators)
    best_model.fit(X_train, y_train)

    # Predict on the test set
    y_pred = best_model.predict(X_test)

    # Calculate RMSE
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # Return model, RMSE, best parameters, and lengths of input lists for unit testing
    return best_model, rmse, (best_max_depth, best_learning_rate, best_n_estimators), (len(data['Sc']), len(data['Fz']), len(data['Dm']), len(data['Ra']))

