import pandas as pd  
import numpy as np  
from scipy.optimize import minimize, OptimizeResult  
from typing import Dict, Tuple

def estimate_keyword_strengths(
    data: pd.DataFrame
) -> Tuple[Dict[str, float], pd.DataFrame, Dict[Tuple[str, str], float], OptimizeResult]:
    data['gpc'] = data['gp'] / data['clicks']
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=['gpc'])
    
    keyword_gpc = data.groupby('keyword')['gpc'].mean().to_dict()
    keywords = list(keyword_gpc.keys())
    num_keywords = len(keywords)
    
    pairwise_stats = {}
    epsilon = 1e-6
    for i in range(num_keywords):
        for j in range(i + 1, num_keywords):
            keyword_i, keyword_j = keywords[i], keywords[j]
            gpc_i, gpc_j = keyword_gpc[keyword_i], keyword_gpc[keyword_j]
            ratio = (gpc_i + epsilon) / (gpc_j + epsilon)
            pairwise_stats[(keyword_i, keyword_j)] = ratio
    
    def neg_log_likelihood(theta):
        likelihood = 0.0
        theta_dict = dict(zip(keywords, theta))
        for (keyword_i, keyword_j), ratio in pairwise_stats.items():
            expected = 1 / (1 + np.exp(-(theta_dict[keyword_i] - theta_dict[keyword_j])))
            observed = 1 if ratio > 1 else 0
            likelihood += observed * np.log(expected + epsilon) + (1 - observed) * np.log(1 - expected + epsilon)
        reg_term = 1e-4 * np.sum(theta ** 2)
        return -likelihood + reg_term
    
    initial_theta = np.zeros(num_keywords)
    opt_result = minimize(neg_log_likelihood, initial_theta, method='BFGS', options={'gtol': 1e-6, 'maxiter': 1000})
    estimated_theta = dict(zip(keywords, opt_result.x))
    
    min_theta = min(estimated_theta.values())
    shift = 1.0 - min_theta if min_theta <= 0 else 0.0
    estimated_theta = {k: v + shift for k, v in estimated_theta.items()}
    
    return estimated_theta, data, pairwise_stats, opt_result
