# No need to update the tests

import unittest
import pandas as pd
import numpy as np
from windows_ideal import generate_area_html

# Unit test class
class TestGenerateAreaHtml(unittest.TestCase):
    def test_generate_html_with_sample_data(self):
        """Test HTML generation with complete data."""
        df1 = pd.DataFrame({
            'Location': ['Store A', 'Store B'],
            'Projection (Units)': [100, 200],
            'Transactions (Units)': [50, 150],
            'SMAPE Value (%)': [20.5, 30.2],
            'Requested (Units)': [80, 120],
            'Received (Units)': [70, 110],
            'Fulfillment Calculation (%)': [90, 92],
            'Out of Stock Count': [5, 3]
        })
        
        # Expected HTML for df1
        expected_html_1 = """
        <tr>
            <td style="border: 1px solid black; text-align: center;">Store A</td>
            <td style="border: 1px solid black; text-align: center;">100</td>
            <td style="border: 1px solid black; text-align: center;">50</td>
            <td style="border: 1px solid black; text-align: center;">20.5</td>  <!-- SMAPE value -->
            <td style="border: 1px solid black; text-align: center;">80</td>
            <td style="border: 1px solid black; text-align: center;">70</td>
            <td style="border: 1px solid black; text-align: center;">90%</td>
            <td style="border: 1px solid black; text-align: center;">5</td>
        </tr>
        
        <tr>
            <td style="border: 1px solid black; text-align: center;">Store B</td>
            <td style="border: 1px solid black; text-align: center;">200</td>
            <td style="border: 1px solid black; text-align: center;">150</td>
            <td style="border: 1px solid black; text-align: center;">30.2</td>  <!-- SMAPE value -->
            <td style="border: 1px solid black; text-align: center;">120</td>
            <td style="border: 1px solid black; text-align: center;">110</td>
            <td style="border: 1px solid black; text-align: center;">92%</td>
            <td style="border: 1px solid black; text-align: center;">3</td>
        </tr>
        """
        self.assertEqual(generate_area_html(df1).strip(), expected_html_1.strip())

    def test_generate_html_with_missing_data(self):
        """Test HTML generation with some missing (NaN) data."""
        df2 = pd.DataFrame({
            'Location': ['Store X'],
            'Projection (Units)': [150],
            'Transactions (Units)': [75],
            'SMAPE Value (%)': [np.nan],
            'Requested (Units)': [np.nan],
            'Received (Units)': [np.nan],
            'Fulfillment Calculation (%)': [85],
            'Out of Stock Count': [np.nan]
        })

        # Expected HTML for df2
        expected_html_2 = """
        <tr>
            <td style="border: 1px solid black; text-align: center;">Store X</td>
            <td style="border: 1px solid black; text-align: center;">150</td>
            <td style="border: 1px solid black; text-align: center;">75</td>
            <td style="border: 1px solid black; text-align: center;">Unavailable</td>  <!-- SMAPE value -->
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">85%</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
        </tr>
        """
        self.assertEqual(generate_area_html(df2).strip(), expected_html_2.strip())

    def test_generate_html_with_all_nan_data(self):
        """Test HTML generation with all NaN values in numeric columns."""
        df3 = pd.DataFrame({
            'Location': ['Store Y'],
            'Projection (Units)': [np.nan],
            'Transactions (Units)': [np.nan],
            'SMAPE Value (%)': [np.nan],
            'Requested (Units)': [np.nan],
            'Received (Units)': [np.nan],
            'Fulfillment Calculation (%)': [np.nan],
            'Out of Stock Count': [np.nan]
        })

        # Expected HTML for df3
        expected_html_3 = """
        <tr>
            <td style="border: 1px solid black; text-align: center;">Store Y</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">Unavailable</td>  <!-- SMAPE value -->
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
            <td style="border: 1px solid black; text-align: center;">0%</td>
            <td style="border: 1px solid black; text-align: center;">0</td>
        </tr>
        """
        self.assertEqual(generate_area_html(df3).strip(), expected_html_3.strip())

# Running the test
if __name__ == '__main__':
    unittest.main(verbosity=2)