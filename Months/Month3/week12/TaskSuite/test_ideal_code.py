import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from testable_ideal_solution import TaskSuite

class TestTaskSuite(unittest.TestCase):

    def setUp(self):
        self.task_suite = TaskSuite()

    @patch('task_suite.TaskSuite.construct_payload')
    @patch('task_suite.TaskSuite.secure_worker_payload')
    @patch('task_suite.TaskSuite.send_with_retry')
    def test_construct_worker_payload_success(self, mock_send, mock_secure, mock_construct):
        #This test ensures the core functionality of constructing a worker payload works correctly under normal conditions
        worker = {
            'InferenceEntrypoint': Mock(),
            'ForecastEntrypoint': Mock(),
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': 100}

        worker['InferenceEntrypoint'].compute.return_value = ('inference_result', None)
        worker['ForecastEntrypoint'].forecast.return_value = ['forecast_result']
        mock_construct.return_value = ({}, None)
        mock_secure.return_value = ({}, None)
        mock_send.return_value = (None, None)

        result, error = self.task_suite.construct_worker_payload(worker, nonce)

        self.assertTrue(result)
        self.assertIsNone(error)

    def test_construct_worker_payload_no_entrypoints(self):
        # It checks how construct_worker_payload handles a worker with the valid entrypoints
        worker = {
            'InferenceEntrypoint': None,
            'ForecastEntrypoint': None
        }
        nonce = {'block_height': 100}

        result, error = self.task_suite.construct_worker_payload(worker, nonce)

        self.assertFalse(result)
        self.assertIsNone(error)

    def test_construct_payload_inference(self):
        # It tests the construction of a payload for inference data
        worker_response = {
            'InfererValue': '10.5',
            'TopicId': 'test_topic'
        }
        height = 100

        result, error = self.task_suite.construct_payload(worker_response, height)

        self.assertIn('Inference', result)
        self.assertEqual(result['Inference']['Value'], Decimal('10.5'))
        self.assertIsNone(error)

    def test_construct_payload_forecast(self):
        # It verifies the construction of a payload for forecast data, including value transformation
        worker_response = {
            'ForecasterValues': [{'value': '5.5', 'worker': 'worker1'}],
            'TopicId': 'test_topic',
            'AllowsNegativeValue': False
        }
        height = 100

        result, error = self.task_suite.construct_payload(worker_response, height)

        self.assertIn('Forecast', result)
        self.assertAlmostEqual(float(result['Forecast']['ForecastElements'][0]['Value']), 1.7047480922384253, places=6)
        self.assertIsNone(error)

    def test_secure_worker_payload(self):
        # It tests the process of securing a worker payload with necessary metadata
        payload = {'test': 'payload'}

        result, error = self.task_suite.secure_worker_payload(payload)

        self.assertEqual(result['Worker'], 'test_address')
        self.assertEqual(result['InferenceForeBundles'], payload)
        self.assertEqual(result['InferencesBundleSignature'], 'signature')
        self.assertEqual(result['Pubkey'], '7075626c69635f6b6579')
        self.assertIsNone(error)

if __name__ == '__main__':
    unittest.main(verbosity=2)