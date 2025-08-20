import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

def compile_verdicts(df):
    # Guarantee 'user_verdict' is treated as object type to accurately handle None values
    df['user_verdict'] = df['user_verdict'].astype('object')

    # Substituting None in 'user_verdict' with a temporary value to account for them in crosstab calculations
    df['user_verdict_temp'] = df['user_verdict'].fillna('NoneVerdict')

    # Generating crosstab that counts occurrences per 'internal_id' and 'user_verdict'
    verdict_sums = pd.crosstab(df['internal_id'], df['user_verdict_temp'])

    # Assuring all expected 'user_verdict' options are present in columns
    for verdict in ['ok', 'investigate', 'NoneVerdict']:
        if verdict not in verdict_sums.columns:
            verdict_sums[verdict] = 0

    # Sorting columns for uniformity
    verdict_sums = verdict_sums[['ok', 'investigate', 'NoneVerdict']]

    # Calculating totals excluding 'NoneVerdict'
    verdict_sums['total_excluding_none'] = verdict_sums['ok'] + verdict_sums['investigate']

    # Defining 'aggregated_verdict' as per your specified criteria
    verdict_sums['compiled_verdict'] = np.where(
        verdict_sums['total_excluding_none'] == 0,
        None,
        np.where(
            verdict_sums['ok'] > verdict_sums['investigate'],
            'ok',
            'investigate'
        )
    )

    # Formatting final DataFrame
    final_df = verdict_sums.reset_index()[['internal_id', 'compiled_verdict']]

    # Converting DataFrame to a list of dictionaries
    final_list = final_df.to_dict(orient='records')

    return final_list

def test_compile_verdicts() -> Tuple[List[pd.DataFrame], List[List[Dict]]]:
    # Test case 1: Sole entry per internal_id with user_verdict as None
    df1 = pd.DataFrame({
        'internal_id': [1],
        'user_verdict': [None],
        'user_signum': [None]
    })
    expected_result1 = [{'internal_id': 1, 'compiled_verdict': None}]

    # Test case 2: Single entry per internal_id with a definite user_verdict
    df2 = pd.DataFrame({
        'internal_id': [2],
        'user_verdict': ['ok'],
        'user_signum': ['user1']
    })
    expected_result2 = [{'internal_id': 2, 'compiled_verdict': 'ok'}]

    # Test case 3: Odd count of entries with a majority verdict
    df3 = pd.DataFrame({
        'internal_id': [3, 3, 3],
        'user_verdict': ['ok', 'ok', 'investigate'],
        'user_signum': ['user1', 'user2', 'user3']
    })
    expected_result3 = [{'internal_id': 3, 'compiled_verdict': 'ok'}]

    # Test case 4: Even count with no clear majority
    df4 = pd.DataFrame({
        'internal_id': [4, 4],
        'user_verdict': ['ok', 'investigate'],
        'user_signum': ['user1', 'user2']
    })
    expected_result4 = [{'internal_id': 4, 'compiled_verdict': 'investigate'}]

    # Test case 5: Assorted scenarios with several internal_ids
    df5 = pd.DataFrame({
        'internal_id': [5, 5, 6, 6, 6],
        'user_verdict': ['ok', 'ok', 'investigate', None, 'investigate'],
        'user_signum': ['user1', 'user2', 'user3', None, 'user4']
    })
    expected_result5 = [
        {'internal_id': 5, 'compiled_verdict': 'ok'},
        {'internal_id': 6, 'compiled_verdict': 'investigate'}
    ]

    # Test case 6: Explicit testing rule adherence where user_signum is None only when user_verdict is None
    df6 = pd.DataFrame({
        'internal_id': [7],
        'user_verdict': ['ok'],
        'user_signum': [None]
    })
    expected_result6 = [{'internal_id': 7, 'compiled_verdict': 'ok'}]

    # Test case 7: Ensuring no multiples by the same user_signum on a single internal_id
    df7 = pd.DataFrame({
        'internal_id': [8, 8],
        'user_verdict': ['ok', 'investigate'],
        'user_signum': ['user1', 'user1']
    })
    expected_result7 = [{'internal_id': 8, 'compiled_verdict': 'investigate'}]

    # Test case 8: Complex scenario with None values and duplicated user_signum across different internal_ids
    df8 = pd.DataFrame({
        'internal_id': [9, 9, 9, 10, 10],
        'user_verdict': [None, 'ok', 'investigate', 'ok', 'ok'],
        'user_signum': [None, 'user2', 'user2', 'user3', 'user4']
    })
    expected_result8 = [
        {'internal_id': 9, 'compiled_verdict': 'investigate'},
        {'internal_id': 10, 'compiled_verdict': 'ok'}
    ]

    return ([df1, df2, df3, df4, df5, df6, df7, df8], 
            [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, 
             expected_result6, expected_result7, expected_result8])
