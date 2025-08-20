import unittest
import pandas as pd
import numpy as np
from forecast_implementation import forecast_all_items, data_partitioning, load_models, forecast_single_article

class TestForecastImplementation(unittest.TestCase):
    def setUp(self):
        # Set up test data and configurations
        self.client_config = {
            "article_level": "article",
            "location_level": "location",
            "forecaster": {"back_test": False}
        }
        self.model_builder_config = {}

    def test_forecast_all_items(self):
        # Test the main forecast_all_items function
        result = forecast_all_items(self.client_config, self.model_builder_config)

        # Check if the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Check if the DataFrame has the expected columns
        expected_columns = ['article', 'location', 'forecast']
        self.assertTrue(all(col in result.columns for col in expected_columns))

        # Check if the DataFrame is not empty
        self.assertTrue(len(result) > 0)

        # Check data types of columns
        self.assertEqual(result['article'].dtype, 'object')
        self.assertEqual(result['location'].dtype, 'object')
        self.assertTrue(np.issubdtype(result['forecast'].dtype, np.number))

    def test_data_partitioning(self):
        # Test the data_partitioning function
        transaction, simulation = data_partitioning(self.client_config, self.model_builder_config)

        # Check if both returned objects are DataFrames
        self.assertIsInstance(transaction, pd.DataFrame)
        self.assertIsInstance(simulation, pd.DataFrame)

        # Check if the DataFrames have the expected columns
        expected_columns = ['id', 'article', 'location']
        self.assertTrue(all(col in transaction.columns for col in expected_columns))
        self.assertTrue(all(col in simulation.columns for col in expected_columns))

    def test_load_models(self):
        # Test the load_models function
        meta_info, model_lookup = load_models(self.client_config)

        # Check if both returned objects are dictionaries
        self.assertIsInstance(meta_info, dict)
        self.assertIsInstance(model_lookup, dict)

    def test_forecast_single_article(self):
        # Test the forecast_single_article function
        transaction, simulation = data_partitioning(self.client_config, self.model_builder_config)
        meta_info, model_lookup = load_models(self.client_config)

        result = forecast_single_article(
            self.client_config,
            'A',
            'X',
            transaction[(transaction.article == 'A') & (transaction.location == 'X')],
            simulation[(simulation.article == 'A') & (simulation.location == 'X')],
            meta_info,
            model_lookup
        )

        # Check if the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Check if the DataFrame has the expected columns
        expected_columns = ['article', 'location', 'forecast']
        self.assertTrue(all(col in result.columns for col in expected_columns))

        # Check if the DataFrame has exactly one row
        self.assertEqual(len(result), 1)

        # Check if the 'forecast' column contains a numeric value
        self.assertTrue(np.issubdtype(result['forecast'].dtype, np.number))

if __name__ == '__main__':
    unittest.main(verbosity=2)