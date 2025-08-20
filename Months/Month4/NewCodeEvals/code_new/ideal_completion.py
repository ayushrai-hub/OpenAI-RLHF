# ideal_completion.py

import numpy as np
from sklearn.feature_selection import mutual_info_regression
from typing import Optional, Tuple, List, Dict, Literal
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error

class ExtremelyAdvancedLinearRegression:
    def __init__(self,
                 learning_rate: float = 0.01,
                 n_iterations: int = 1000,
                 regularization: Literal['none', 'l1', 'l2', 'elastic_net'] = 'none',
                 lambda_reg: float = 0.1,
                 l1_ratio: float = 0.5,
                 optimizer: Literal['sgd', 'adam', 'rmsprop'] = 'adam',
                 polynomial_degree: int = 1,
                 batch_size: Optional[int] = None,
                 early_stopping: bool = False,
                 patience: int = 10,
                 feature_selection: bool = False,
                 n_features_to_select: Optional[int] = None):
        
        # Parameter validation
        if learning_rate <= 0:
            raise ValueError("Learning rate must be positive")
        if polynomial_degree < 1:
            raise ValueError("Polynomial degree must be at least 1")
        if batch_size is not None and batch_size <= 0:
            raise ValueError("Batch size must be positive")
        if patience < 0:
            raise ValueError("Patience must be non-negative")
        if n_features_to_select is not None and n_features_to_select < 1:
            raise ValueError("Number of features to select must be positive")
        if regularization not in ['none', 'l1', 'l2', 'elastic_net']:
            raise ValueError("Invalid regularization type")
        if optimizer not in ['sgd', 'adam', 'rmsprop']:
            raise ValueError("Invalid optimizer type")

        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.regularization = regularization
        self.lambda_reg = lambda_reg
        self.l1_ratio = l1_ratio
        self.optimizer = optimizer
        self.polynomial_degree = polynomial_degree
        self.batch_size = batch_size
        self.early_stopping = early_stopping
        self.patience = patience
        self.feature_selection = feature_selection
        self.n_features_to_select = n_features_to_select
        self.weights = None
        self.bias = None
        self.scaler = StandardScaler()
        self.poly_features = PolynomialFeatures(degree=polynomial_degree, include_bias=False)
        self.training_loss = []
        self.selected_features = None

    def _initialize_parameters(self, n_features: int) -> None:
        self.weights = np.random.randn(n_features) * 0.01  # Changed from zeros to small random values
        self.bias = 0
        if self.optimizer in ['adam', 'rmsprop']:
            self.m = np.zeros(n_features)
            self.v = np.zeros(n_features)
            self.beta1 = 0.9
            self.beta2 = 0.999
            self.epsilon = 1e-8
            self.t = 0

    def _compute_gradients(self, X: np.ndarray, y: np.ndarray, y_pred: np.ndarray) -> Tuple[np.ndarray, float]:
        n_samples = X.shape[0]
        dw = (1 / n_samples) * np.dot(X.T, (y_pred - y))
        db = (1 / n_samples) * np.sum(y_pred - y)

        if self.regularization == 'l2':
            dw += (self.lambda_reg / n_samples) * self.weights
        elif self.regularization == 'l1':
            dw += (self.lambda_reg / n_samples) * np.sign(self.weights)
        elif self.regularization == 'elastic_net':
            dw += (self.lambda_reg / n_samples) * (
                self.l1_ratio * np.sign(self.weights) + (1 - self.l1_ratio) * self.weights)

        return dw, db

    def _update_parameters(self, dw: np.ndarray, db: float) -> None:
        if self.optimizer == 'sgd':
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
        elif self.optimizer == 'adam':
            self.t += 1
            self.m = self.beta1 * self.m + (1 - self.beta1) * dw
            self.v = self.beta2 * self.v + (1 - self.beta2) * (dw ** 2)
            m_hat = self.m / (1 - self.beta1 ** self.t)
            v_hat = self.v / (1 - self.beta2 ** self.t)
            self.weights -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
            self.bias -= self.learning_rate * db
        elif self.optimizer == 'rmsprop':
            self.v = self.beta2 * self.v + (1 - self.beta2) * (dw ** 2)
            self.weights -= self.learning_rate * dw / (np.sqrt(self.v) + self.epsilon)
            self.bias -= self.learning_rate * db

    def _select_features(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        mi_scores = mutual_info_regression(X, y)
        if self.n_features_to_select is None:
            self.n_features_to_select = X.shape[1] // 2
        idxs = np.argsort(mi_scores)[-self.n_features_to_select:]
        self.selected_features = idxs
        return X[:, idxs]

    def _validate_input(self, X: np.ndarray, y: np.ndarray, X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None) -> None:
        if len(X) == 0 or len(y) == 0:
            raise ValueError("Empty dataset provided")
        
        if np.any(np.isnan(X)) or np.any(np.isnan(y)):
            raise ValueError("Input contains NaN values")
        
        if np.any(np.isinf(X)) or np.any(np.isinf(y)):
            raise ValueError("Input contains infinity values")
        
        if len(X) != len(y):
            raise ValueError("Mismatched dimensions between X and y")
        
        # Modified zero variance check - skip for single samples
        if len(X) > 1 and np.any(np.std(X, axis=0) == 0):
            raise ValueError("Zero variance features detected")
            
        if self.early_stopping:
            if X_val is None or y_val is None:
                raise ValueError("Validation data required when early stopping is enabled")
            if X_val.shape[1] != X.shape[1]:
                raise ValueError("Validation data has different number of features")
    def fit(self,
            X: np.ndarray,
            y: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'ExtremelyAdvancedLinearRegression':
        
        # Convert inputs to numpy arrays and validate
        X = np.asarray(X)
        y = np.asarray(y)
        
        try:
            X = X.astype(float)
            y = y.astype(float)
        except (ValueError, TypeError):
            raise ValueError("Non-numeric input detected")

        self._validate_input(X, y, X_val, y_val)

        if self.feature_selection:
            X = self._select_features(X, y)
            if X_val is not None:
                X_val = X_val[:, self.selected_features]

        X_poly = self.poly_features.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_poly)
        n_samples, n_features = X_scaled.shape

        self._initialize_parameters(n_features)

        best_val_loss = float('inf')
        patience_counter = 0

        for iteration in range(self.n_iterations):
            if self.batch_size:
                indices = np.random.choice(n_samples, self.batch_size, replace=False)
                X_batch = X_scaled[indices]
                y_batch = y[indices]
            else:
                X_batch = X_scaled
                y_batch = y

            y_pred = np.dot(X_batch, self.weights) + self.bias
            dw, db = self._compute_gradients(X_batch, y_batch, y_pred)
            self._update_parameters(dw, db)

            loss = mean_squared_error(y_batch, y_pred)
            self.training_loss.append(loss)

            if self.early_stopping and X_val is not None and y_val is not None:
                X_val_poly = self.poly_features.transform(X_val)
                X_val_scaled = self.scaler.transform(X_val_poly)
                y_val_pred = np.dot(X_val_scaled, self.weights) + self.bias
                val_loss = mean_squared_error(y_val, y_val_pred)
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.patience:
                        break
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None or self.bias is None:
            raise AttributeError("Model has not been fitted yet.")
        if self.feature_selection:
            X = X[:, self.selected_features]
        X_poly = self.poly_features.transform(X)
        X_scaled = self.scaler.transform(X_poly)
        return np.dot(X_scaled, self.weights) + self.bias

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        y_pred = self.predict(X)
        return r2_score(y, y_pred)