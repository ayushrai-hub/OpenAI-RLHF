import pandas as pd

# Custom aggregation function
def mm_diff_col(x):
    return x.max() - x.min()

# Function to be unit tested
def get_agg(df: pd.DataFrame, col_name: str) -> pd.Series:
    return df.agg(
        median=pd.NamedAgg(column=col_name, aggfunc='median'),
        mean=pd.NamedAgg(column=col_name, aggfunc='mean'),
        mm_diff=pd.NamedAgg(column=col_name, aggfunc=mm_diff_col),
        count=pd.NamedAgg(column=col_name, aggfunc='count')
    )
