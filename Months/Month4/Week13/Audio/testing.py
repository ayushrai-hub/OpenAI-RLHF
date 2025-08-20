import unittest
import numpy as np
from new import EnhancedAdaptiveBeamformer
class TestEnhancedAdaptiveBeamformer(unittest.TestCase):
    def setUp(self):
        """Initialize the beamformer and common test signals"""
        self.beamformer = EnhancedAdaptiveBeamformer(
            num_mics=4,
            mic_distance=0.05,
            sample_rate=16000,
            sound_speed=343
        )
        
        # Create test signals
        duration = 1.0  # seconds
        t = np.linspace(0, duration, int(self.beamformer.sample_rate * duration))
        self.target_signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        self.noise_signal = np.random.normal(0, 0.1, len(self.target_signal))

    def test_initialization(self):
        """Test if the beamformer initializes with correct parameters"""
        self.assertEqual(self.beamformer.num_mics, 4)
        self.assertEqual(self.beamformer.sample_rate, 16000)
        self.assertAlmostEqual(self.beamformer.mic_distance, 0.05)
        self.assertAlmostEqual(self.beamformer.sound_speed, 343)

    def test_simulate_microphone_signals(self):
        """Test if microphone signal simulation works correctly"""
        doa_angles = [0, 30, 60, 90]
        signals = self.beamformer.simulate_microphone_signals(
            self.target_signal,
            self.noise_signal,
            doa_angles
        )
        
        # Check shape
        self.assertEqual(signals.shape[0], self.beamformer.num_mics)
        self.assertEqual(signals.shape[1], len(self.target_signal))
        
        # Check if signals are different for different microphones
        for i in range(self.beamformer.num_mics - 1):
            self.assertFalse(np.allclose(signals[i], signals[i+1]))
            
        # Check signal amplitude range
        self.assertTrue(np.all(np.abs(signals) <= np.max(np.abs(self.target_signal)) + np.max(np.abs(self.noise_signal))))

    def test_estimate_doa(self):
        """Test if DOA estimation works within reasonable bounds"""
        # Test with known DOA
        test_angle = 30.0
        signals = self.beamformer.simulate_microphone_signals(
            self.target_signal,
            self.noise_signal,
            [0, test_angle, 60, 90]
        )
        
        estimated_doa = self.beamformer.estimate_doa(signals)
        
        # Check if estimated DOA is a float
        self.assertIsInstance(estimated_doa, float)
        
        # Check if estimated DOA is within reasonable bounds (-90 to 90 degrees)
        self.assertTrue(-90 <= estimated_doa <= 90)
        
        # Check if estimation is roughly accurate (within 20 degrees)
        self.assertLess(abs(estimated_doa - test_angle), 20)

    def test_apply_beamforming(self):
        """Test if beamforming produces valid output"""
        signals = self.beamformer.simulate_microphone_signals(
            self.target_signal,
            self.noise_signal,
            [0, 30, 60, 90]
        )
        doa = self.beamformer.estimate_doa(signals)
        beamformed_signal = self.beamformer.apply_beamforming(signals, doa)
        
        # Check output shape
        self.assertEqual(len(beamformed_signal), len(self.target_signal))
        
        # Check if output is not all zeros
        self.assertFalse(np.allclose(beamformed_signal, 0))
        
        # Check if output magnitude is reasonable
        self.assertTrue(np.all(np.abs(beamformed_signal) <= np.max(np.abs(signals))))

    def test_process_frame(self):
        """Test if frame processing works end-to-end"""
        frame = self.target_signal[:1024]  # Test with a shorter frame
        beamformed_signal, doa = self.beamformer.process_frame(frame)
        
        # Check output types
        self.assertIsInstance(beamformed_signal, np.ndarray)
        self.assertIsInstance(doa, float)
        
        # Check if DOA is within bounds
        self.assertTrue(-90 <= doa <= 90)
        
        # Check if output signal has reasonable values
        self.assertFalse(np.any(np.isnan(beamformed_signal)))
        self.assertFalse(np.any(np.isinf(beamformed_signal)))

    def test_process_for_model(self):
        """Test if model-specific processing works"""
        for model_type in ["wake_word", "local_command", "cloud"]:
            processed_signal = self.beamformer.process_for_model(
                self.target_signal,
                model_type
            )
            
            # Check output shape
            self.assertEqual(len(processed_signal), len(self.target_signal))
            
            # Check if output is not all zeros
            self.assertFalse(np.allclose(processed_signal, 0))
            
            # Check if output is finite
            self.assertTrue(np.all(np.isfinite(processed_signal)))

    def test_noise_suppression(self):
        """Test if noise suppression maintains signal integrity"""
        for noise_type in ["tv", "vacuum", "kitchen"]:
            suppressed_signal = self.beamformer.suppress_noise(
                self.target_signal,
                noise_type
            )
            
            # Check if output shape matches input
            self.assertEqual(len(suppressed_signal), len(self.target_signal))
            
            # Check if output is not all zeros
            self.assertFalse(np.allclose(suppressed_signal, 0))
            
            # Check if output magnitude is reasonable
            self.assertTrue(np.all(np.abs(suppressed_signal) <= np.max(np.abs(self.target_signal))))

    def test_error_handling(self):
        """Test if the system handles errors appropriately"""
        # Test with wrong number of channels
        wrong_signals = np.random.randn(3, 1000)  # Only 3 channels instead of 4
        with self.assertRaises(ValueError):
            _ = self.beamformer.apply_beamforming(wrong_signals, 30.0)
        
        # Test with invalid DOA angle
        signals = np.random.randn(4, 1000)
        with self.assertRaises(ValueError):
            _ = self.beamformer.apply_beamforming(signals, 91.0)  # DOA > 90 degrees

if __name__ == '__main__':
    unittest.main(verbosity=2)