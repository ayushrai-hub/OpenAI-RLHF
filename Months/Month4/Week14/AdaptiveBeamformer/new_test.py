import unittest
import numpy as np
from testable_ideal_completion import AdaptiveBeamformer

class TestAdaptiveBeamformer(unittest.TestCase):
    def setUp(self):
        # It sets up test fixtures before each test method.
        # It initializes the beamformer with standard audio processing parameters.
        self.beamformer = AdaptiveBeamformer(
            num_mics=4,
            mic_distance=0.05,
            sample_rate=16000,
            use_subband=True,
            num_bands=8
        )
        
        # It generates test signals:
        self.test_duration = 0.1  # 100ms
        self.num_samples = int(self.beamformer.sample_rate * self.test_duration)
        t = np.linspace(0, self.test_duration, self.num_samples)
        self.test_signal = 0.5 * np.sin(2 * np.pi * 1000 * t) + 0.3  # Non-zero mean sinusoid
        self.test_noise = 0.1 * np.random.randn(self.num_samples)  # Small random noise
        self.test_angles = [0, 45, 90]
        
        # Create multi-channel data with small random variations
        # This simulates slightly imperfect mic recordings while maintaining correlation
        self.test_signals = np.array([
            self.test_signal,
            self.test_signal + 0.01 * np.random.randn(self.num_samples),
            self.test_signal + 0.01 * np.random.randn(self.num_samples),
            self.test_signal + 0.01 * np.random.randn(self.num_samples)
        ])

    def test_initialization(self):
        # It verifies that the beamformer initializes with correct parameters.
        # Check if constructor properly sets all the basic parameters
        self.assertEqual(self.beamformer.num_mics, 4)
        self.assertEqual(self.beamformer.sample_rate, 16000)
        self.assertTrue(self.beamformer.use_subband)
        self.assertEqual(self.beamformer.num_bands, 8)

    def test_fixed_point_conversion(self):
        # It tests the conversion between floating-point and fixed-point representations.
        test_data = np.array([0.5, -0.5, 0.1, -0.1])
        fixed_point = self.beamformer.to_fixed_point(test_data)
        float_data = self.beamformer.from_fixed_point(fixed_point)
        
        # It verifies that the fixed-point values stay within 24-bit integer range (-2^23 to 2^23-1).
        self.assertTrue(np.all(fixed_point >= -8388608))
        self.assertTrue(np.all(fixed_point <= 8388607))
        
        # It verifies the conversion is reversible within acceptable precision (3 decimal places).
        np.testing.assert_array_almost_equal(test_data, float_data, decimal=3)

    def test_subband_decomposition(self):
        # It verifies that the subband analysis filter bank operation.
        test_signal = self.test_signal + 0.01
        subbands = self.beamformer.subband_decomposition(test_signal)
        
        # It verifies that the output dimensions match expected subband structure
        self.assertEqual(subbands.shape[0], self.beamformer.num_bands)
        expected_length = len(test_signal) // self.beamformer.num_bands
        self.assertEqual(subbands.shape[1], expected_length)

    def test_doa_estimation(self):
        # It Test the Direction of Arrival (DOA) estimation algorithm
        signals = self.test_signals + 0.1 * np.random.randn(*self.test_signals.shape)
        doa = self.beamformer.estimate_doa(signals)
        
        # It checks if estimated angle is within physical limits (-90° to +90°)
        self.assertGreaterEqual(doa, -90)
        self.assertLessEqual(doa, 90)

    def test_adaptive_weights(self):
        # It tests the calculation of adaptive beamforming weights
        signals = self.test_signals + 0.1 * np.random.randn(*self.test_signals.shape)
        weights = self.beamformer.adaptive_weights(signals, 45)
        
        # Verify weight vector dimensions match number of microphones
        self.assertEqual(len(weights), self.beamformer.num_mics)
        
        # Verify weights are scaled appropriately for 24-bit fixed-point
        self.assertTrue(np.all(weights >= -8388608))
        self.assertTrue(np.all(weights <= 8388607))

    def test_process_output_shape(self):
        # It Verifies that the beamformed output maintains correct signal length"""
        # Process signals with added noise for realistic conditions
        signals = self.test_signals + 0.1 * np.random.randn(*self.test_signals.shape)
        output = self.beamformer.process(signals)
        
        # Verify output length matches input length
        self.assertEqual(len(output), signals.shape[1])

    def test_performance_metrics(self):
        # It tests the calculation of various performance metrics
        # Process signals with noise for realistic evaluation
        signals = self.test_signals + 0.1 * np.random.randn(*self.test_signals.shape)
        output = self.beamformer.process(signals)
        
        # Use slightly noisy reference for realistic correlation
        reference = signals[0] + 0.01 * np.random.randn(len(signals[0]))
        
        # It calculates comprehensive set of performance metrics
        metrics = self.beamformer.evaluate_performance(reference, output)
        
        # Verify all required metrics are present
        required_metrics = ['SNR', 'MSE', 'Speech_Clarity', 'Envelope_Correlation',
                          'PESQ_like', 'STOI_like', 'Latency', 'Memory_Usage']
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            
        # Verify metric values are valid (not NaN)
        self.assertFalse(np.isnan(metrics['SNR']))
        self.assertFalse(np.isnan(metrics['MSE']))
        self.assertFalse(np.isnan(metrics['Speech_Clarity']))
        self.assertFalse(np.isnan(metrics['Envelope_Correlation']))

if __name__ == '__main__':
    unittest.main(verbosity=2)