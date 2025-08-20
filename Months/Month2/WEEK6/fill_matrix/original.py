import numpy as np
from scipy.special import logsumexp
from sklearn.mixture import GaussianMixture

def fill_matrix(X: np.ndarray, mixture: GaussianMixture, decimal_places: int = 6) -> np.ndarray:
    n, d = X.shape
    K = mixture.means_.shape[0]
    mu, var, pi = mixture.means_, mixture.covariances_, mixture.weights_
    
    # Create the completed matrix, initially a copy of X
    X_pred = np.copy(X)
    
    for i in range(n):
        # Identify the observed and missing entries
        observed = X[i] != 0
        missing = ~observed
        
        if np.any(missing):
            # Compute log-likelihoods for the observed entries
            log_likelihood = np.zeros(K)
            
            for k in range(K):
                # Use only observed entries
                diff = X[i, observed] - mu[k, observed]
                
                # Calculate log-likelihood for the observed data
                log_likelihood[k] = np.log(pi[k]) - 0.5 * np.sum((diff ** 2) / var[k][observed])
                log_likelihood[k] -= 0.5 * np.sum(observed) * np.log(2 * np.pi * var[k][observed]).sum()
            
            # Convert log-likelihoods to responsibilities
            log_responsibilities = log_likelihood - logsumexp(log_likelihood)
            responsibilities = np.exp(log_responsibilities)
            
            # Estimate missing values as the weighted sum of component means
            X_pred[i, missing] = np.sum(responsibilities[:, np.newaxis] * mu[:, missing], axis=0)
    
    # Round the predicted values to the specified number of decimal places
    X_pred = np.round(X_pred, decimals=decimal_places)
    
    return X_pred
