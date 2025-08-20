import pandas as pd
import unittest
from ideal_completion import replicate_rows

class TestDataframeModification(unittest.TestCase):

    def test_no_error(self):
        # Sample data for df1
        data1 = {
            'A': ['Total', 'Total', 'X'],
            'B': ['Y', 'Total', 'Total'],
            'C': [1, 2, 3]
        }

        # Sample data for df2
        data2 = {
            'A': ['P', 'Q', 'R'],
            'B': ['Y', 'Z', 'W'],
            'C': [4, 5, 6]
        }

        # Convert to DataFrame
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        # Array with columns to check for 'Total'
        array = ['A', 'B']

        replicate_rows(df1, df2, array)

    def test_replicate_rows_count(self):
        # Sample data for df1
        data1 = {
            'A': ['Total', 'Total', 'X'],
            'B': ['Y', 'Total', 'Total'],
            'C': [1, 2, 3]
        }

        # Sample data for df2
        data2 = {
            'A': ['P', 'Q', 'R'],
            'B': ['Y', 'Z', 'W'],
            'C': [4, 5, 6]
        }

        # Convert to DataFrame
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        # Array with columns to check for 'Total'
        array = ['A', 'B']

        modified_df = replicate_rows(df1, df2, array)

        all_total_rows = 0
        for _, row in df1.iterrows():
            # Check if the row has 'Total' in the specified columns
            if all(row[col] == 'Total' for col in array):
                all_total_rows += 1
        expected_rows = len(df1) - all_total_rows  + len(df2) * all_total_rows

        self.assertEqual(len(modified_df), expected_rows)

if __name__ == '__main__':
    unittest.main(verbosity=2)