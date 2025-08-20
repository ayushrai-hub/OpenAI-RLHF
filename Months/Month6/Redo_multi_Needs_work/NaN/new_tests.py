import unittest
import pandas as pd
import numpy as np
from ideal_completion import generate_area_html

class TestGenerateAreaHtml(unittest.TestCase):
    def normalize_html(self, html_str):
        """Normalize HTML string for comparison by removing extra whitespace and newlines."""
        # Split into lines and strip each line
        lines = [line.strip() for line in html_str.split('\n')]
        # Remove empty lines
        lines = [line for line in lines if line]
        # Join back together
        return '\n'.join(lines)
    
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
        
        result = self.normalize_html(generate_area_html(df1))
        
        expected_parts = [
            '<tr>',
            '<td style="border: 1px solid black; text-align: center;">Store A</td>',
            '<td style="border: 1px solid black; text-align: center;">100</td>',
            '<td style="border: 1px solid black; text-align: center;">50</td>',
            '<td style="border: 1px solid black; text-align: center;">20.5</td>',
            '<td style="border: 1px solid black; text-align: center;">80</td>',
            '<td style="border: 1px solid black; text-align: center;">70</td>',
            '<td style="border: 1px solid black; text-align: center;">90%</td>',
            '<td style="border: 1px solid black; text-align: center;">5</td>',
            '</tr>',
            '<tr>',
            '<td style="border: 1px solid black; text-align: center;">Store B</td>',
            '<td style="border: 1px solid black; text-align: center;">200</td>',
            '<td style="border: 1px solid black; text-align: center;">150</td>',
            '<td style="border: 1px solid black; text-align: center;">30.2</td>',
            '<td style="border: 1px solid black; text-align: center;">120</td>',
            '<td style="border: 1px solid black; text-align: center;">110</td>',
            '<td style="border: 1px solid black; text-align: center;">92%</td>',
            '<td style="border: 1px solid black; text-align: center;">3</td>',
            '</tr>'
        ]
        
        for part in expected_parts:
            self.assertIn(self.normalize_html(part), result)

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

        result = self.normalize_html(generate_area_html(df2))
        
        expected_parts = [
            '<tr>',
            '<td style="border: 1px solid black; text-align: center;">Store X</td>',
            '<td style="border: 1px solid black; text-align: center;">150</td>',
            '<td style="border: 1px solid black; text-align: center;">75</td>',
            '<td style="border: 1px solid black; text-align: center;">Unavailable</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">85%</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '</tr>'
        ]
        
        for part in expected_parts:
            self.assertIn(self.normalize_html(part), result)

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

        result = self.normalize_html(generate_area_html(df3))
        
        expected_parts = [
            '<tr>',
            '<td style="border: 1px solid black; text-align: center;">Store Y</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">Unavailable</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '<td style="border: 1px solid black; text-align: center;">0%</td>',
            '<td style="border: 1px solid black; text-align: center;">0</td>',
            '</tr>'
        ]
        
        for part in expected_parts:
            self.assertIn(self.normalize_html(part), result)

if __name__ == '__main__':
    unittest.main(verbosity=2)