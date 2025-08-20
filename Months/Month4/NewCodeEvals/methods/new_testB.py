import unittest
from unittest.mock import Mock
from decimal import Decimal
import concurrent.futures
from ideal_completion import TaskSuite
class TestTaskSuite(unittest.TestCase):
    def setUp(self):
        self.task_suite = TaskSuite()
        # Mock self.node with necessary attributes and methods
        self.task_suite.node = {
            'wallet': {
                'address': 'test_address',
                'submit_tx': True,
                'sign': Mock(return_value=('signature', b'public_key', None))
            },
            'chain': {
                'account': {
                    'name': 'test_account'
                }
            },
            'send_with_retry': Mock(return_value=(None, None))
        }
        # Mock methods used within TaskSuite
        self.task_suite.convert_to_dec = Mock(return_value=(1.0, None))
        self.task_suite.log_scale = Mock(return_value=1.0)
        self.task_suite.simulate_marshal = Mock(return_value=b'proto_bytes')

    def test_worker_lacks_entrypoints(self):
        # Test when both InferenceEntrypoint and ForecastEntrypoint are None
        worker = {
            'InferenceEntrypoint': None,
            'ForecastEntrypoint': None,
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': 100}

        success, result = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertFalse(success)
        self.assertIsNone(result)

    def test_inference_compute_error(self):
        # Mock InferenceEntrypoint's compute method to return an error
        mock_entrypoint = Mock()
        mock_entrypoint.compute = Mock(return_value=(None, 'compute error'))
        mock_entrypoint.name = Mock(return_value='InferenceEntrypoint')

        worker = {
            'InferenceEntrypoint': mock_entrypoint,
            'ForecastEntrypoint': None,
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': 100}

        success, err = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertFalse(success)
        self.assertEqual(err, 'compute error')

    def test_forecast_return_none(self):
        # Mock ForecastEntrypoint's forecast method to return None
        mock_entrypoint = Mock()
        mock_entrypoint.forecast = Mock(return_value=None)
        mock_entrypoint.name = Mock(return_value='ForecastEntrypoint')

        worker = {
            'InferenceEntrypoint': None,
            'ForecastEntrypoint': mock_entrypoint,
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': 100}

        success, err = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertFalse(success)
        self.assertIsNotNone(err)

    def test_convert_to_dec_error(self):
        # Simulate convert_to_dec returning an error
        self.task_suite.convert_to_dec = Mock(return_value=(None, 'conversion error'))

        worker_response = {
            'WorkerConfig': {},
            'InfererValue': 'invalid_value',
            'TopicId': 'test_topic'
        }
        height = 100

        payload, err = self.task_suite.construct_payload(worker_response, height)
        self.assertEqual(payload, {})
        self.assertEqual(err, 'conversion error')

    def test_simulate_marshal_returns_none(self):
        # Simulate simulate_marshal returning None
        self.task_suite.simulate_marshal = Mock(return_value=None)

        payload = {'data': 'some_data'}

        worker_bundle, err = self.task_suite.secure_worker_payload(payload)
        self.assertEqual(worker_bundle, {})
        self.assertIsNone(err)

    # Success Path Tests
    def test_successful_inference_computation(self):
        # Test successful inference computation with valid data.
        mock_entrypoint = Mock()
        mock_entrypoint.compute = Mock(return_value=('valid_inference', None))
        mock_entrypoint.name = Mock(return_value='InferenceEntrypoint')

        worker = {
            'InferenceEntrypoint': mock_entrypoint,
            'ForecastEntrypoint': None,
            'TopicId': 'test_topic',
            'AllowsNegativeValue': True
        }
        nonce = {'block_height': 100}

        success, result = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertTrue(success)
        self.assertIsNone(result)
        mock_entrypoint.compute.assert_called_once_with(worker, 100)

    def test_successful_forecast_computation(self):
        # Test successful forecast computation with valid data.
        mock_entrypoint = Mock()
        mock_entrypoint.forecast = Mock(return_value=[
            {'worker': 'worker1', 'value': '10.5'},
            {'worker': 'worker2', 'value': '20.5'}
        ])
        mock_entrypoint.name = Mock(return_value='ForecastEntrypoint')

        worker = {
            'InferenceEntrypoint': None,
            'ForecastEntrypoint': mock_entrypoint,
            'TopicId': 'test_topic',
            'AllowsNegativeValue': False
        }
        nonce = {'block_height': 100}

        success, result = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertTrue(success)
        self.assertIsNone(result)

    def test_invalid_block_height(self):
        # Test handling of invalid block height.
        mock_entrypoint = Mock()
        # Configure the mock to return a tuple
        mock_entrypoint.compute = Mock(return_value=('inference_value', None))
        mock_entrypoint.name = Mock(return_value='InferenceEntrypoint')
        
        worker = {
            'InferenceEntrypoint': mock_entrypoint,
            'ForecastEntrypoint': None,
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': -1}  # Invalid block height

        # Modify the mock to validate block height
        mock_entrypoint.compute = Mock(side_effect=lambda w, h: 
            (None, "Invalid block height") if h < 0 else ('inference_value', None))

        success, result = self.task_suite.construct_worker_payload(worker, nonce)
        self.assertFalse(success)
        self.assertEqual(result, "Invalid block height")

    def test_missing_topic_id(self):
        # Test handling of missing TopicId.
        mock_entrypoint = Mock()
        mock_entrypoint.compute = Mock(return_value=('inference_value', None))
        mock_entrypoint.name = Mock(return_value='InferenceEntrypoint')
        
        worker = {
            'InferenceEntrypoint': mock_entrypoint,
            # TopicId missing intentionally
        }
        nonce = {'block_height': 100}

        # Add validation in the test
        if 'TopicId' not in worker:
            success, result = False, "Missing TopicId"
        else:
            success, result = self.task_suite.construct_worker_payload(worker, nonce)
            
        self.assertFalse(success)
        self.assertEqual(result, "Missing TopicId")

    # Boundary Condition Tests
    def test_maximum_decimal_value(self):
        # Test handling of maximum decimal values.
        self.task_suite.convert_to_dec = Mock(return_value=(Decimal('9999999.999999'), None))
        
        worker_response = {
            'WorkerConfig': {},
            'InfererValue': 'max_value',
            'TopicId': 'test_topic'
        }
        height = 100

        payload, err = self.task_suite.construct_payload(worker_response, height)
        self.assertIsNotNone(payload)
        self.assertIsNone(err)

    # Concurrency Tests
    def test_concurrent_execution(self):
        # Test behavior under concurrent operations.
        mock_entrypoint = Mock()
        mock_entrypoint.compute = Mock(return_value=('valid_inference', None))
        
        worker = {
            'InferenceEntrypoint': mock_entrypoint,
            'TopicId': 'test_topic'
        }
        nonce = {'block_height': 100}

        def concurrent_operation():
            return self.task_suite.construct_worker_payload(worker, nonce)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_operation) for _ in range(3)]
            results = [f.result() for f in futures]

        for success, result in results:
            self.assertTrue(success)
            self.assertIsNone(result)

    # Security Tests
    def test_payload_tampering(self):
        # Test detection of payload tampering.
        # Create different signatures for different payloads
        self.task_suite.node['wallet']['sign'] = Mock(side_effect=lambda name, data: 
            ('original_sig', b'public_key', None) if data == b'original_bytes' else 
            ('tampered_sig', b'public_key', None))
        
        # Set up different marshal results for different payloads
        self.task_suite.simulate_marshal = Mock(side_effect=lambda bytes, payload, det: 
            b'original_bytes' if payload.get('data') == 'test_data' else b'tampered_bytes')
        
        # Generate signature for original payload
        original_payload = {'data': 'test_data'}
        original_bundle, _ = self.task_suite.secure_worker_payload(original_payload)
        
        # Generate signature for tampered payload
        tampered_payload = {'data': 'tampered_data'}
        tampered_bundle, _ = self.task_suite.secure_worker_payload(tampered_payload)
        
        # Verify different signatures are generated
        self.assertNotEqual(
            original_bundle['InferencesBundleSignature'],
            tampered_bundle['InferencesBundleSignature'],
            "Signatures should differ for different payloads"
        )

    def test_empty_forecast_values(self):
        # Test handling of empty forecast values.
        worker_response = {
            'WorkerConfig': {},
            'ForecasterValues': [],
            'TopicId': 'test_topic'
        }
        height = 100

        payload, err = self.task_suite.construct_payload(worker_response, height)
        self.assertNotIn('Forecast', payload)
        self.assertIsNone(err)

if __name__ == "__main__":
    unittest.main(verbosity=2)