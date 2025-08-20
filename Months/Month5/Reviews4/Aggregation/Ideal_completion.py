# ideal_completion.py

import pandas as pd

# Custom aggregation function
def mm_diff_col(x):
    return x.max() - x.min()

def get_agg(df: pd.DataFrame, col_name: str) -> pd.Series:
    return df[col_name].agg([
        'median',
        'mean',
        mm_diff_col,
        'count'
    ])