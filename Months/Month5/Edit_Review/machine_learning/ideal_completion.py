# ideal_completion.py

import numpy as np

class SimpleDecisionTree:
    def __init__(self, max_depth=1):
        self.max_depth = max_depth
        self.n_classes_ = None
        self.tree_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.n_classes_ = len(np.unique(y))
        self.tree_ = self._build_tree(X, y, depth=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict(inputs, self.tree_) for inputs in X])

    def _gini(self, y: np.ndarray) -> float:
        """Calculates Gini impurity."""
        m = len(y)
        return 1.0 - sum((np.sum(y == c) / m) ** 2 for c in np.unique(y))

    def _best_split(self, X: np.ndarray, y: np.ndarray):
        """Finds the best feature and threshold for splitting."""
        m, n = X.shape
        if m <= 1:
            return None, None
        parent_gini = self._gini(y)
        best_gini = parent_gini
        best_idx, best_thr = None, None

        for idx in range(n):
            thresholds, classes = zip(*sorted(zip(X[:, idx], y)))
            num_left = [0] * self.n_classes_
            num_right = [np.sum(y == c) for c in range(self.n_classes_)]
            for i in range(1, m):
                c = classes[i - 1]
                if c < self.n_classes_:
                    num_left[c] += 1
                    num_right[c] -= 1
                gini_left = 1.0 - sum((num_left[x] / i) ** 2 for x in range(self.n_classes_) if i > 0)
                gini_right = 1.0 - sum((num_right[x] / (m - i)) ** 2 for x in range(self.n_classes_) if m - i > 0)
                gini = (i * gini_left + (m - i) * gini_right) / m
                if thresholds[i] == thresholds[i - 1]:
                    continue
                if gini < best_gini:
                    best_gini = gini
                    best_idx = idx
                    best_thr = (thresholds[i] + thresholds[i - 1]) / 2
        return best_idx, best_thr

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int):
        """Recursively builds the decision tree."""
        num_samples_per_class = [np.sum(y == i) for i in range(max(self.n_classes_, np.max(y) + 1))]
        predicted_class = np.argmax(num_samples_per_class)
        node = {'type': 'leaf', 'class': predicted_class}

        if depth < self.max_depth:
            idx, thr = self._best_split(X, y)
            if idx is not None:
                indices_left = X[:, idx] <= thr
                X_left, y_left = X[indices_left], y[indices_left]
                X_right, y_right = X[~indices_left], y[~indices_left]
                if len(y_left) > 0 and len(y_right) > 0:
                    node = {
                        'type': 'node',
                        'feature_index': idx,
                        'threshold': thr,
                        'left': self._build_tree(X_left, y_left, depth + 1),
                        'right': self._build_tree(X_right, y_right, depth + 1)
                    }
        return node

    def _predict(self, inputs: np.ndarray, tree: dict) -> int:
        """Traverses the tree to make a prediction."""
        if tree['type'] == 'leaf':
            return tree['class']
        if inputs[tree['feature_index']] <= tree['threshold']:
            return self._predict(inputs, tree['left'])
        else:
            return self._predict(inputs, tree['right'])

class SimpleLogisticRegression:
    def __init__(self, lr=0.01, n_iter=100):
        self.lr = lr
        self.n_iter = n_iter
        self.weights = None
        self.is_trained = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fits the logistic regression model to the data."""
        self.weights = np.zeros(X.shape[1] + 1)
        if self.n_iter == 0:
            self.is_trained = False
            return

        X = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-8)
        X_bias = np.hstack([np.ones((X.shape[0], 1)), X])

        for _ in range(self.n_iter):
            z = np.dot(X_bias, self.weights)
            y_pred = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
            gradient = np.dot(X_bias.T, (y_pred - y)) / y.size
            self.weights -= self.lr * gradient

        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts binary labels for input data."""
        if self.weights is None:
            raise ValueError("Model has not been trained. Call `fit` before prediction.")

        if not self.is_trained:
            return np.zeros(X.shape[0], dtype=int)

        X = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-8)
        X_bias = np.hstack([np.ones((X.shape[0], 1)), X])
        z = np.dot(X_bias, self.weights)
        y_pred = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
        return (y_pred >= 0.5).astype(int)