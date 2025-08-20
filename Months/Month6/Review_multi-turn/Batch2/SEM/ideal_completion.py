import pandas as pd
import numpy as np
import itertools
from math import log
from scipy.optimize import minimize
from typing import Dict, Tuple
from scipy.optimize import OptimizeResult

def estimate_keyword_strengths(
    data: pd.DataFrame
) -> Tuple[Dict[str, float], pd.DataFrame, Dict[Tuple[str, str], float], OptimizeResult]:
    # Make a copy to avoid modifying original data
    df = data.copy()
    # Compute gpc (gross profit per click)
    # Avoid division by zero
    df['gpc'] = df.apply(lambda row: row['gp'] / row['clicks'] if row['clicks'] > 0 else 0.0, axis=1)
    # Unique keywords
    keywords = sorted(df['keyword'].unique().tolist())
    # Compute pairwise stats
    pairwise_stats: Dict[Tuple[str, str], float] = {}
    # Use mean gpc per keyword
    avg_gpc = {k: df[df['keyword'] == k]['gpc'].mean() for k in keywords}
    for k1, k2 in itertools.permutations(keywords, 2):
        # Compute ratio k1 vs k2
        gpc1 = avg_gpc[k1]
        gpc2 = avg_gpc[k2]
        if (k1, k2) not in pairwise_stats:  # for permutations fill both directions
            if gpc1 + gpc2 > 0:
                pairwise_stats[(k1, k2)] = gpc1 / (gpc1 + gpc2)
            else:
                pairwise_stats[(k1, k2)] = 0.0

    # Optimize using Bradley Terry model
    # We'll estimate log theta for each keyword
    key_index = {k: i for i, k in enumerate(keywords)}
    def neg_log_likelihood(params):
        thetas = np.exp(params)  # positive
        ll = 0.0
        for (i1,i2) in itertools.combinations(keywords, 2):
            p12 = thetas[key_index[i1]]/(thetas[key_index[i1]]+thetas[key_index[i2]])
            p21 = thetas[key_index[i2]]/(thetas[key_index[i1]]+thetas[key_index[i2]])
            # Observed probabilities
            obs12 = pairwise_stats.get((i1,i2),0.0)
            obs21 = pairwise_stats.get((i2,i1),0.0)
            # Contribute to log-likelihood
            # We treat these as pseudo-counts
            if obs12>0:
                ll += obs12 * np.log(p12+1e-12)
            if obs21>0:
                ll += obs21 * np.log(p21+1e-12)
        return -ll

    initial_params = np.zeros(len(keywords))
    res = minimize(neg_log_likelihood, initial_params, method='BFGS')
    theta_values = dict()
    if res.success:
        theta_hat = np.exp(res.x)
        for k in keywords:
            theta_values[k] = theta_hat[key_index[k]]
    else:
        # fallback: use initial
        for k in keywords:
            theta_values[k] = 1.0

    return theta_values, df, pairwise_stats, res
