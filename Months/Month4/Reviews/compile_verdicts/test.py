import unittest
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from testableIc import test_compile_verdicts


def compile_verdicts(df):
    """
    Ideal compile_verdicts method that follows every rule and generates resultant list of dictionaries.
    """
    # Validation checks to ensure df meets criteria
    if (
        not df['internal_id'].notna().all() or                   # Check that all internal_id values are non-null
        not df.groupby(['internal_id', 'user_signum']).size().le(1).all() or  # Ensure no duplicate user_signum per internal_id
        not df['user_verdict'].isin(['ok', 'investigate', None]).all()        # Validate user_verdict values
    ):
        return []  # Return an empty list if criteria are not met

    # Guarantee 'user_verdict' is treated as object type to accurately handle None values
    df['user_verdict'] = df['user_verdict'].astype('object')

    # Substitute None in 'user_verdict' with a temporary value to account for them in crosstab calculations
    df['user_verdict_temp'] = df['user_verdict'].fillna('NoneVerdict')

    # Generate crosstab that counts occurrences per 'internal_id' and 'user_verdict'
    verdict_sums = pd.crosstab(df['internal_id'], df['user_verdict_temp'])

    # Ensure all expected 'user_verdict' options are present in columns
    for verdict in ['ok', 'investigate', 'NoneVerdict']:
        if verdict not in verdict_sums.columns:
            verdict_sums[verdict] = 0

    # Sort columns for uniformity
    verdict_sums = verdict_sums[['ok', 'investigate', 'NoneVerdict']]

    # Calculate totals excluding 'NoneVerdict'
    verdict_sums['total_excluding_none'] = verdict_sums['ok'] + verdict_sums['investigate']

    # Define 'compiled_verdict' based on criteria
    verdict_sums['compiled_verdict'] = np.where(
        verdict_sums['total_excluding_none'] == 0,
        None,
        np.where(
            verdict_sums['ok'] > verdict_sums['investigate'],
            'ok',
            'investigate'
        )
    )

    # Format final DataFrame
    final_df = verdict_sums.reset_index()[['internal_id', 'compiled_verdict']]

    # Convert DataFrame to a list of dictionaries
    final_list = final_df.to_dict(orient='records')

    return final_list


class TestCompileVerdicts(unittest.TestCase):
    def setUp(self):
        # Get the test data and expected results from test_compile_verdicts
        self.dataframes, self.expected_results = test_compile_verdicts()

    def validate_df(self, df: pd.DataFrame) -> bool:
        """
        Validates the DataFrame according to specified rules:
        - Columns and data types must be correct
        - Only specific values allowed in user_verdict
        - None in user_verdict should have None in user_signum
        - No duplicate user_signum per internal_id
        """
        # Rule 1: Check for required columns and their data types
        if not all(col in df.columns for col in ['user_verdict', 'user_signum', 'internal_id']):
            return False
        if df['internal_id'].dtype != 'int64' or df['user_verdict'].dtype != 'object':
            return False

        # Rule 2: user_verdict should only have specific values
        if not df['user_verdict'].isin(['ok', 'investigate', None]).all():
            return False

        # Rule 3: None in user_verdict should have None in user_signum
        if not df[df['user_verdict'].isna()]['user_signum'].isna().all():
            return False

        # Rule 4: The same user_signum cannot submit multiple verdicts on the same internal_id
        duplicates = df[df['user_signum'].notna()].duplicated(subset=['internal_id', 'user_signum'])
        if duplicates.any():
            return False

        return True

    def test_all_dataframes_are_valid(self):
        """
        Validates each DataFrame in self.dataframes to ensure all are valid.
        If any DataFrame is invalid, the test fails.
        """
        for i, df in enumerate(self.dataframes):
            with self.subTest(i=i):
                self.assertTrue(self.validate_df(df), f"DataFrame at index {i} is invalid")
                
    def test_compile_verdicts_output_matches_expected(self):
        """
        Validates that the output of compile_verdicts for each DataFrame matches the expected result.
        Assumes that all DataFrames have been validated as valid in test_all_dataframes_are_valid.
        """
        for i, df in enumerate(self.dataframes):
            with self.subTest(i=i):
                result = compile_verdicts(df)
                self.assertEqual(result, self.expected_results[i], f"Mismatch in output for DataFrame at index {i}")
    
    def test_multiple_test_scenarios(self):
        """
        Ensures that there are multiple test cases to check the robustness of the compile_verdicts function.
        """
        self.assertGreater(len(self.dataframes), 1, "Expected more than one DataFrame for testing.")

    def test_dataframe_and_expectation_count_match(self):
        """
        Confirms that the number of DataFrames matches the number of expected results to ensure one-to-one comparison.
        """
        self.assertEqual(len(self.dataframes), len(self.expected_results), 
                         "Mismatch between number of test DataFrames and expected results.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
