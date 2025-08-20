import unittest
import numpy as np
from ideal_completion import EnhancedAdaptiveBeamformer

class TestEnhancedAdaptiveBeamformer(unittest.TestCase):
    def setUp(self):
        self.beamformer = EnhancedAdaptiveBeamformer(
            num_mics=4,
            mic_distance=0.05,
            sample_rate=16000,
            sound_speed=343
        )
        
        # Create test signals
        self.frame_size = self.beamformer.FRAME_SIZE
        t = np.linspace(0, 0.064, self.frame_size)
        self.clean_signal = np.sin(2 * np.pi * 1000 * t)
        self.mic_signals = np.zeros((4, self.frame_size))
        
        # Add delayed versions of clean signal to each channel
        for i in range(4):
            delay = i * 2
            self.mic_signals[i] = np.roll(self.clean_signal, delay)
            self.mic_signals[i] += np.random.normal(0, 0.1, self.frame_size)
    
    def test_doa_estimation(self):
        """Test direction of arrival estimation"""
        doa = self.beamformer.estimate_doa(self.mic_signals)
        self.assertTrue(-90 <= doa <= 90)
    
    def test_beamforming(self):
        """Test beamforming operation"""
        doa = 30.0
        enhanced = self.beamformer.apply_beamforming(self.mic_signals, doa)
        self.assertEqual(enhanced.shape, (self.frame_size,))
    
    def test_noise_suppression(self):
        """Test noise suppression for different noise types"""
        signal = self.mic_signals[0]
        for noise_type in ["tv", "vacuum", "kitchen"]:
            suppressed = self.beamformer.suppress_noise(signal, noise_type)
            self.assertEqual(suppressed.shape, signal.shape)
    
    def test_frame_processing(self):
        """Test complete frame processing pipeline"""
        enhanced, doa = self.beamformer.process_frame(self.mic_signals, "tv")
        
        self.assertEqual(enhanced.shape, (self.frame_size,))
        self.assertTrue(-90 <= doa <= 90)
    
    def test_model_specific_processing(self):
        """Test processing for different voice recognition models"""
        test_audio = np.random.randn(self.frame_size)
        
        for model_type in ["wake_word", "local_command", "cloud"]:
            processed = self.beamformer.process_for_model(test_audio, model_type)
            self.assertEqual(processed.shape, test_audio.shape)
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        # Test invalid frame shape
        invalid_frame = np.random.randn(3, self.frame_size)  # Wrong number of mics
        with self.assertRaises(ValueError):
            self.beamformer.process_frame(invalid_frame)
        
        # Test invalid model type
        with self.assertRaises(ValueError):
            self.beamformer.process_for_model(self.clean_signal, "invalid_model")

if __name__ == '__main__':
    unittest.main(verbosity=2)