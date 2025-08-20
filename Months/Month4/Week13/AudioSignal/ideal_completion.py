# ideal_completion.py

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

class Int24:
    MAX_VALUE = 8388607  # 2^23 - 1
    MIN_VALUE = -8388608  # -2^23
    
    @staticmethod
    def clip(value):
        return np.clip(value, Int24.MIN_VALUE, Int24.MAX_VALUE)
    
    @staticmethod
    def to_int24(float_val):
        scaled = np.round(float_val * 8388607.0)
        return Int24.clip(scaled).astype(np.int32)
    
    @staticmethod
    def from_int24(int24_val):
        return (int24_val.astype(np.float32) / 8388607.0)

@dataclass
class NoiseProfile:
    type: str
    frequency_range: Tuple[float, float]
    amplitude_pattern: np.ndarray

class NoiseProfiles:
    TV_SOUND = NoiseProfile(
        type="tv",
        frequency_range=(100, 4000),
        amplitude_pattern=np.array([0.8, 0.6, 0.4, 0.3])
    )
    VACUUM = NoiseProfile(
        type="vacuum",
        frequency_range=(50, 1000),
        amplitude_pattern=np.array([0.9, 0.85, 0.8, 0.75])
    )
    KITCHEN = NoiseProfile(
        type="kitchen",
        frequency_range=(200, 2000),
        amplitude_pattern=np.array([0.7, 0.5, 0.3, 0.2])
    )

class EmbeddedDNN:
    def __init__(self, input_size: int = 1024, hidden_size: int = 64):
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Initialize weights with int24 precision
        self.W1 = Int24.to_int24(np.random.randn(input_size, hidden_size) * 0.01)
        self.b1 = Int24.to_int24(np.zeros(hidden_size))
        self.W2 = Int24.to_int24(np.random.randn(hidden_size, input_size) * 0.01)
        self.b2 = Int24.to_int24(np.zeros(input_size))
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def sigmoid(self, x):
        x = np.clip(x, -10, 10)
        return 1 / (1 + np.exp(-x))
    
    def forward(self, x):
        if len(x.shape) == 1:
            x = x.reshape(1, -1)
        
        x_int24 = Int24.to_int24(x)
        h1 = self.relu(np.dot(x_int24, self.W1) + self.b1)
        h1 = Int24.to_int24(h1)
        out = self.sigmoid(np.dot(h1, self.W2) + self.b2)
        out = Int24.to_int24(out)
        return Int24.from_int24(out).flatten()

class VoiceModelInterface:
    def __init__(self, model_type: str):
        self.model_type = model_type
        
    def preprocess(self, audio: np.ndarray) -> np.ndarray:
        if self.model_type == "wake_word":
            return self._preprocess_wake_word(audio)
        elif self.model_type == "local_command":
            return self._preprocess_local_command(audio)
        else:  # cloud
            return self._preprocess_cloud(audio)
    
    def _preprocess_wake_word(self, audio: np.ndarray) -> np.ndarray:
        audio_int24 = Int24.to_int24(audio)
        window_size = 5
        filtered = np.convolve(Int24.from_int24(audio_int24), 
                             np.ones(window_size)/window_size, 
                             mode='same')
        return Int24.to_int24(filtered)
    
    def _preprocess_local_command(self, audio: np.ndarray) -> np.ndarray:
        audio_int24 = Int24.to_int24(audio)
        alpha = 0.95
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        for i in range(1, len(audio)):
            filtered[i] = alpha * (filtered[i-1] + audio[i] - audio[i-1])
        return Int24.to_int24(filtered)
    
    def _preprocess_cloud(self, audio: np.ndarray) -> np.ndarray:
        return Int24.to_int24(audio)

class EnhancedAdaptiveBeamformer:
    def __init__(self, 
                num_mics: int = 4,
                mic_distance: float = 0.05, 
                sample_rate: int = 16000,
                sound_speed: float = 343):
        
        self.NUM_MICS = num_mics
        self.MIC_DISTANCE = mic_distance
        self.SAMPLE_RATE = sample_rate 
        self.SOUND_SPEED = sound_speed
        self.FRAME_SIZE = 1024
        
        self.noise_suppressor = EmbeddedDNN(self.FRAME_SIZE)
        self.voice_models = {
            "wake_word": VoiceModelInterface("wake_word"),
            "local_command": VoiceModelInterface("local_command"),
            "cloud": VoiceModelInterface("cloud")
        }
        self.noise_profiles = {
            "tv": NoiseProfiles.TV_SOUND,
            "vacuum": NoiseProfiles.VACUUM,
            "kitchen": NoiseProfiles.KITCHEN
        }
    
    def estimate_doa(self, signals: np.ndarray) -> float:
        sig1 = signals[0, :self.FRAME_SIZE]
        sig2 = signals[1, :self.FRAME_SIZE]
        
        sig1 = Int24.from_int24(Int24.to_int24(sig1))
        sig2 = Int24.from_int24(Int24.to_int24(sig2))
        
        window = np.hanning(len(sig1))
        sig1 = sig1 * window
        sig2 = sig2 * window
        
        X1 = np.fft.rfft(sig1)
        X2 = np.fft.rfft(sig2)
        gcc = X1 * np.conj(X2)
        gcc_phat = gcc / (np.abs(gcc) + 1e-12)
        tau = np.fft.irfft(gcc_phat)
        
        max_tau = np.argmax(np.abs(tau))
        if max_tau > self.FRAME_SIZE//2:
            max_tau -= self.FRAME_SIZE
        
        delay = max_tau / self.SAMPLE_RATE
        max_delay = self.MIC_DISTANCE / self.SOUND_SPEED
        delay = np.clip(delay, -max_delay, max_delay)
        angle = np.arcsin(delay * self.SOUND_SPEED / self.MIC_DISTANCE)
        
        return np.rad2deg(angle)
    
    def apply_beamforming(self, signals: np.ndarray, doa_angle: float) -> np.ndarray:
        """Improved delay-and-sum beamforming"""
        angle_rad = np.deg2rad(doa_angle)
        num_samples = signals.shape[1]
        
        # Improved array geometry calculation
        positions = np.arange(self.NUM_MICS) - (self.NUM_MICS - 1)/2
        positions *= self.MIC_DISTANCE
        delays = positions * np.sin(angle_rad) / self.SOUND_SPEED
        delay_samples = np.round(delays * self.SAMPLE_RATE).astype(int)
        
        # Improved signal alignment
        aligned = np.zeros((self.NUM_MICS, num_samples))
        for i in range(self.NUM_MICS):
            if delay_samples[i] >= 0:
                aligned[i, delay_samples[i]:] = signals[i, :-delay_samples[i] if delay_samples[i] > 0 else None]
            else:
                aligned[i, :delay_samples[i]] = signals[i, -delay_samples[i]:]
        
        # Apply Hamming window for better sidelobe suppression
        window = np.hamming(self.NUM_MICS)[:, np.newaxis]
        enhanced = np.sum(aligned * window, axis=0) / np.sum(window)
        
        return Int24.to_int24(enhanced)
    
    def suppress_noise(self, signal: np.ndarray, noise_type: str) -> np.ndarray:
        """Improved noise suppression with spectral subtraction"""
        profile = self.noise_profiles[noise_type]
        signal_float = Int24.from_int24(signal)
        
        # Compute FFT
        signal_freq = np.fft.rfft(signal_float)
        freqs = np.fft.rfftfreq(len(signal_float), 1/self.SAMPLE_RATE)
        
        # Create frequency-dependent suppression mask
        mask = np.ones_like(freqs)
        freq_band = (freqs >= profile.frequency_range[0]) & (freqs <= profile.frequency_range[1])
        
        # Apply gradual suppression based on noise profile
        suppression = np.interp(freqs[freq_band], 
                            np.linspace(profile.frequency_range[0], profile.frequency_range[1], len(profile.amplitude_pattern)),
                            profile.amplitude_pattern)
        mask[freq_band] = 1 - 0.7 * suppression  # Reduced suppression factor
        
        # Apply mask and convert back to time domain
        filtered_freq = signal_freq * mask
        filtered = np.fft.irfft(filtered_freq)
        
        return Int24.to_int24(filtered)
    
    def process_frame(self, frame: np.ndarray, noise_type: Optional[str] = None) -> Tuple[np.ndarray, float]:
        if frame.shape[0] != self.NUM_MICS:
            raise ValueError(f"Expected {self.NUM_MICS} channels, got {frame.shape[0]}")
        
        if frame.shape[1] != self.FRAME_SIZE:
            raise ValueError(f"Expected frame size {self.FRAME_SIZE}, got {frame.shape[1]}")
            
        frame_int24 = Int24.to_int24(frame)
        doa = self.estimate_doa(frame_int24)
        enhanced = self.apply_beamforming(frame_int24, doa)
        
        if noise_type and noise_type in self.noise_profiles:
            enhanced = self.suppress_noise(enhanced, noise_type)
        
        enhanced = enhanced[:self.FRAME_SIZE]
        enhanced = self.noise_suppressor.forward(Int24.from_int24(enhanced))
        
        return enhanced, doa
    
    def process_for_model(self, audio: np.ndarray, model_type: str) -> np.ndarray:
        """Process audio for specific voice recognition model type"""
        if model_type not in self.voice_models:
            raise ValueError(f"Unsupported model type: {model_type}")
        return self.voice_models[model_type].preprocess(audio)

def test_system():
    beamformer = EnhancedAdaptiveBeamformer()
    
    # Generate test signals with improved SNR and signal characteristics
    duration = beamformer.FRAME_SIZE / beamformer.SAMPLE_RATE
    sample_rate = beamformer.SAMPLE_RATE
    t = np.linspace(0, duration, beamformer.FRAME_SIZE)
    
    # Create a more realistic speech-like signal
    f0 = 200  # fundamental frequency for speech
    harmonics = [1, 2, 3, 4]
    clean_signal = np.zeros_like(t)
    for h in harmonics:
        clean_signal += np.sin(2 * np.pi * f0 * h * t) / h
    
    # Normalize signal
    clean_signal = 0.7 * clean_signal / np.max(np.abs(clean_signal))
    
    true_doa = 30.0  # degrees
    
    # Generate multichannel signals with better SNR
    mic_signals = np.zeros((beamformer.NUM_MICS, beamformer.FRAME_SIZE))
    
    # Calculate target input SNR of 20 dB
    signal_power = np.mean(clean_signal**2)
    desired_snr = 20.0  # dB
    noise_power = signal_power / (10 ** (desired_snr/10))
    noise_level = np.sqrt(noise_power)
    
    # Calculate delays with corrected geometry
    positions = np.arange(beamformer.NUM_MICS) - (beamformer.NUM_MICS - 1)/2
    positions *= beamformer.MIC_DISTANCE
    delays = positions * np.sin(np.deg2rad(true_doa)) / beamformer.SOUND_SPEED
    delay_samples = np.round(delays * sample_rate).astype(int)
    
    # Apply delays and add calibrated noise
    for i in range(beamformer.NUM_MICS):
        delayed_signal = np.roll(clean_signal, delay_samples[i])
        noise = np.random.normal(0, noise_level, beamformer.FRAME_SIZE)
        mic_signals[i] = delayed_signal + noise
    
    noise_types = ["tv", "vacuum", "kitchen"]
    
    for noise_type in noise_types:
        print(f"\nTesting with {noise_type} noise:")
        
        try:
            # Process the frame
            enhanced_signal, estimated_doa = beamformer.process_frame(
                mic_signals, 
                noise_type=noise_type
            )
            
            # Calculate SNR metrics with proper scaling
            clean_power = np.mean(clean_signal**2)
            input_noise_power = np.mean(noise**2)
            enhanced_noise_power = np.mean((enhanced_signal - clean_signal)**2)
            
            input_snr = 10 * np.log10(clean_power / input_noise_power)
            output_snr = 10 * np.log10(clean_power / enhanced_noise_power)
            
            # Process with different models
            for model_type in ["wake_word", "local_command", "cloud"]:
                processed = beamformer.process_for_model(
                    enhanced_signal, 
                    model_type
                )
                print(f"Processed for {model_type} model")
            
            print(f"True DOA: {true_doa:.1f}°")
            print(f"Estimated DOA: {estimated_doa:.1f}°")
            print(f"Input SNR: {input_snr:.1f} dB")
            print(f"Output SNR: {output_snr:.1f} dB")
            print(f"SNR Improvement: {(output_snr - input_snr):.1f} dB")
            
        except Exception as e:
            print(f"Error processing {noise_type} noise: {str(e)}")

if __name__ == "__main__":
    test_system()



jhjhh