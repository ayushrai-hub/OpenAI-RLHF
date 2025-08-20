import unittest
from unittest.mock import patch
from testableIC import FinancialAnalytics 

class TestFinancialAnalytics(unittest.TestCase):

    def setUp(self):
        self.fa = FinancialAnalytics()
        self.attributes = ['profit', 'quantity', 'margin']
        self.intervals = ['this_year', 'last_year']
        self.conditions = ['actual', 'budget']
        self.durations = ['monthly', 'ytd']
        self.cycles = ["current", "january", "february", "march"]

    @patch('logging.error')
    def test_calc_variance_logs_error(self, mock_logging_error):
        # Simulating an error while calculating variance and ensuring it's logged
        with patch.object(self.fa, '_calc_column_total', side_effect=Exception('Test error')):
            result = self.fa._calc_variance('col1', 'col2')
            self.assertIsNone(result)
            mock_logging_error.assert_called_once_with('Error calculating variance for col1 and col2: Test error')

    @patch('logging.error')
    def test_calc_percentage_logs_error(self, mock_logging_error):
        # Simulating an error while calculating percentage and ensuring it's logged
        with patch.object(self.fa, '_calc_column_total', side_effect=Exception('Test error')):
            result = self.fa._calc_percentage('col1', 'col2')
            self.assertIsNone(result)
            mock_logging_error.assert_called_once_with('Error calculating percentage for col1 and col2: Test error')

    @patch('logging.info')
    def test_create_methods_logs_info(self, mock_logging_info):
        # Verifying that create_methods logs info during its execution
        self.fa.create_methods(self.attributes, self.intervals, self.conditions, self.durations, self.cycles)
        self.assertGreater(mock_logging_info.call_count, 0)

    def test_format_currency(self):
        # Testing that the format method correctly formats currency
        result = self.fa.format(1000.5, "currency")
        self.assertEqual(result, "$1,000.50")

    def test_format_percentage(self):
        # Testing that the format method correctly formats percentages
        result = self.fa.format(12.34, "percentage")
        self.assertEqual(result, "12.34%")

    def test_format_default(self):
        # Testing that the format method returns the default value if format type is 'other'
        result = self.fa.format(1234, "other")
        self.assertEqual(result, 1234)


if __name__ == '__main__':
    unittest.main(verbosity=2)
