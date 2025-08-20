

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
        
        # Changed from uppercase to lowercase to match test cases
        self.num_mics = num_mics
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate 
        self.sound_speed = sound_speed
        self.frame_size = 1024
        
        self.noise_suppressor = EmbeddedDNN(self.frame_size)
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
    
    def simulate_microphone_signals(self, target_signal: np.ndarray, noise_signal: np.ndarray, doa_angles: list) -> np.ndarray:
        """Added method to match test requirements"""
        mic_signals = np.zeros((self.num_mics, len(target_signal)))
        for i in range(self.num_mics):
            delay = (self.mic_distance * i * np.cos(np.deg2rad(doa_angles[i]))) / self.sound_speed
            delay_samples = int(delay * self.sample_rate)
            mic_signals[i, delay_samples:delay_samples+len(target_signal)] += target_signal
            mic_signals[i, :len(noise_signal)] += noise_signal
        return mic_signals

    def estimate_doa(self, signals: np.ndarray) -> float:
        sig1 = signals[0]
        sig2 = signals[1]
        
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
        if max_tau > len(sig1)//2:
            max_tau -= len(sig1)
        
        delay = max_tau / self.sample_rate
        max_delay = self.mic_distance / self.sound_speed
        delay = np.clip(delay, -max_delay, max_delay)
        angle = np.arcsin(delay * self.sound_speed / self.mic_distance)
        
        return np.rad2deg(angle)
    
    def apply_beamforming(self, signals: np.ndarray, doa_angle: float) -> np.ndarray:
        """Modified to include input validation"""
        if signals.shape[0] != self.num_mics:
            raise ValueError(f"Expected {self.num_mics} channels")
        if abs(doa_angle) > 90:
            raise ValueError("DOA angle must be between -90 and 90 degrees")
            
        angle_rad = np.deg2rad(doa_angle)
        num_samples = signals.shape[1]
        
        positions = np.arange(self.num_mics) - (self.num_mics - 1)/2
        positions *= self.mic_distance
        delays = positions * np.sin(angle_rad) / self.sound_speed
        delay_samples = np.round(delays * self.sample_rate).astype(int)
        
        aligned = np.zeros((self.num_mics, num_samples))
        for i in range(self.num_mics):
            if delay_samples[i] >= 0:
                aligned[i, delay_samples[i]:] = signals[i, :-delay_samples[i] if delay_samples[i] > 0 else None]
            else:
                aligned[i, :delay_samples[i]] = signals[i, -delay_samples[i]:]
        
        window = np.hamming(self.num_mics)[:, np.newaxis]
        enhanced = np.sum(aligned * window, axis=0) / np.sum(window)
        
        return Int24.to_int24(enhanced)
    
    def suppress_noise(self, signal: np.ndarray, noise_type: str) -> np.ndarray:
        """Modified to handle noise_type validation"""
        if noise_type not in self.noise_profiles:
            raise ValueError(f"Unsupported noise type: {noise_type}")
            
        profile = self.noise_profiles[noise_type]
        signal_float = Int24.from_int24(signal) if isinstance(signal, np.ndarray) else signal
        
        signal_freq = np.fft.rfft(signal_float)
        freqs = np.fft.rfftfreq(len(signal_float), 1/self.sample_rate)
        
        mask = np.ones_like(freqs)
        freq_band = (freqs >= profile.frequency_range[0]) & (freqs <= profile.frequency_range[1])
        
        suppression = np.interp(freqs[freq_band], 
                            np.linspace(profile.frequency_range[0], profile.frequency_range[1], len(profile.amplitude_pattern)),
                            profile.amplitude_pattern)
        mask[freq_band] = 1 - 0.7 * suppression
        
        filtered_freq = signal_freq * mask
        filtered = np.fft.irfft(filtered_freq)
        
        return Int24.to_int24(filtered)
    
    def process_frame(self, frame: np.ndarray, noise_type: Optional[str] = None) -> Tuple[np.ndarray, float]:
        # Convert single channel input to multichannel if needed
        if len(frame.shape) == 1:
            frame = np.tile(frame, (self.num_mics, 1))
            
        frame_int24 = Int24.to_int24(frame)
        doa = self.estimate_doa(frame_int24)
        enhanced = self.apply_beamforming(frame_int24, doa)
        
        if noise_type and noise_type in self.noise_profiles:
            enhanced = self.suppress_noise(enhanced, noise_type)
        
        enhanced = enhanced[:self.frame_size]
        enhanced = self.noise_suppressor.forward(Int24.from_int24(enhanced))
        
        return enhanced, doa
    
    def process_for_model(self, audio: np.ndarray, model_type: str) -> np.ndarray:
        if model_type not in self.voice_models:
            raise ValueError(f"Unsupported model type: {model_type}")
        return self.voice_models[model_type].preprocess(audio)
    

    