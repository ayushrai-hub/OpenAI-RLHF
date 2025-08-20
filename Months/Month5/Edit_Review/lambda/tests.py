import unittest
from unittest.mock import patch, MagicMock
from ideal_completion import lambda_processor, initiate_airflow_process


class TestLambdaProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_logger = patch('logging.getLogger', return_value=MagicMock()).start()
        self.mock_boto3_client = patch('boto3.client').start()
        self.mock_http_client = patch('http.client.HTTPSConnection').start()

        # Mock environment variables
        patch('os.environ', {
            'ENVIRONMENT': 'test',
            'AREA_NAME': 'test_area',
            'AREA_CODE': '001',
            'TARGET_ENV': 'test_env',
            'DATABASE_CONNECTION': 'test_connection',
            'SITE': 'test_site',
            'STRUCTURE': 'test_structure'
        }).start()

        # Mock helper functions
        self.mock_execute_query = patch('ideal_completion.execute_query').start()
        self.mock_perform_query = patch('ideal_completion.perform_query').start()
        self.mock_get_process_executions = patch('ideal_completion.get_process_executions', return_value=(True, ["exec1"], ["id1"], "20240101")).start()

        # Mock Airflow client and its behavior
        self.mock_airflow_client = MagicMock()
        self.mock_airflow_client.create_cli_token.return_value = {
            'WebServerHostname': 'test-host',
            'CliToken': 'test-token'
        }
        self.mock_boto3_client.return_value = self.mock_airflow_client

        # Mock HTTP client response
        self.mock_http_conn = MagicMock()
        self.mock_http_conn.getresponse.return_value.read.return_value = b"{'stdout': 'dGVzdCBvdXRwdXQ='}"  
        self.mock_http_client.return_value = self.mock_http_conn

    def tearDown(self):
        patch.stopall()

    def test_lambda_processor_successful_execution(self):  
        # Test successful execution of lambda_processor
        self.mock_execute_query.side_effect = lambda *_: [("table1", 1), ("table2", 1)]
        result = lambda_processor({"key": "value"}, {})
        self.assertEqual(result, "Lambda process completed.")
        self.mock_execute_query.assert_called()
        self.mock_perform_query.assert_called()

    def test_lambda_processor_parent_table_pending(self):  
        # Test lambda_processor with pending parent table status
        self.mock_execute_query.side_effect = lambda *_: [("parent_table1", 0), ("parent_table2", 1)]
        result = lambda_processor({"key": "value"}, {})
        self.assertEqual(result, "Lambda process completed.")
        self.mock_perform_query.assert_not_called()

    def test_initiate_airflow_process_valid_input(self):  
        # Test initiate_airflow_process with valid inputs
        result = initiate_airflow_process("test_process", {"key": "value"}, "test_env", self.mock_airflow_client)
        self.assertEqual(result.decode("utf-8"), "test output")
        self.mock_http_conn.request.assert_called()

    def test_initiate_airflow_process_invalid_token(self):  
        # Test initiate_airflow_process with token generation failure
        self.mock_airflow_client.create_cli_token.side_effect = Exception("Token generation failed")
        with self.assertRaises(Exception):
            initiate_airflow_process("test_process", {"key": "value"}, "test_env", self.mock_airflow_client)

    def test_lambda_processor_unexpected_query_result(self):  
        # Test lambda_processor with unexpected query results
        self.mock_execute_query.side_effect = lambda *_: [("unexpected_table", 0)]
        result = lambda_processor({"key": "value"}, {})
        self.assertEqual(result, "Lambda process completed.")
        self.mock_perform_query.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)