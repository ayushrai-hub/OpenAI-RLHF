import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass

class Int24:
    MAX_VALUE: int = 8388607  # 2^23 - 1
    MIN_VALUE: int = -8388608  # -2^23

    @staticmethod
    def clip(value: np.ndarray) -> np.ndarray:
        return np.clip(value, Int24.MIN_VALUE, Int24.MAX_VALUE)

    @staticmethod
    def to_int24(float_val: np.ndarray) -> np.ndarray:
        return Int24.clip((float_val * Int24.MAX_VALUE).astype(np.int32))

    @staticmethod
    def from_int24(int24_val: np.ndarray) -> np.ndarray:
        return (int24_val / Int24.MAX_VALUE).astype(np.float32)


@dataclass
class NoiseProfile:
    type: str
    frequencies: np.ndarray  # Array of frequencies
    amplitude_pattern: np.ndarray  # Amplitude response corresponding to the frequencies

    @staticmethod
    def create(type: str, frequency_range: Tuple[float, float], amplitude_pattern: np.ndarray) -> "NoiseProfile":
        num_points = len(amplitude_pattern)
        frequencies = np.linspace(frequency_range[0], frequency_range[1], num_points)
        return NoiseProfile(type=type, frequencies=frequencies, amplitude_pattern=amplitude_pattern)


class NoiseProfiles:
    profiles = {
        "tv": NoiseProfile.create("tv", (100, 5000), np.array([1.0, 0.8, 0.6, 0.4])),
        "vacuum": NoiseProfile.create("vacuum", (50, 400), np.array([0.9, 0.7, 0.5, 0.3])),
        "kitchen": NoiseProfile.create("kitchen", (100, 1000), np.array([0.8, 0.6, 0.4, 0.2])),
    }


class EmbeddedDNN:
    def __init__(self, input_size: int = 1024, hidden_size: int = 64):
        self.weights1 = np.random.randn(input_size, hidden_size)
        self.weights2 = np.random.randn(hidden_size, hidden_size)
        self.bias1 = np.zeros(hidden_size)
        self.bias2 = np.zeros(hidden_size)

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    def forward(self, x: np.ndarray) -> np.ndarray:
        x = self.relu(np.dot(x, self.weights1) + self.bias1)
        return self.sigmoid(np.dot(x, self.weights2) + self.bias2)


class VoiceModelInterface:
    def __init__(self, model_type: str):
        self.model_type = model_type

    def preprocess(self, audio: np.ndarray) -> np.ndarray:
        if self.model_type == "wake_word":
            return self._preprocess_wake_word(audio)
        elif self.model_type == "local_command":
            return self._preprocess_local_command(audio)
        elif self.model_type == "cloud":
            return self._preprocess_cloud(audio)
        else:
            raise ValueError("Unknown model type")

    def _preprocess_wake_word(self, audio: np.ndarray) -> np.ndarray:
        return audio * 0.5

    def _preprocess_local_command(self, audio: np.ndarray) -> np.ndarray:
        return audio * 0.75

    def _preprocess_cloud(self, audio: np.ndarray) -> np.ndarray:
        return audio * 1.0


class EnhancedAdaptiveBeamformer:
    FRAME_SIZE: int = 1024  # Frame size in samples (0.064 seconds at 16kHz)

    def __init__(self, num_mics: int = 4, mic_distance: float = 0.05, sample_rate: int = 16000, sound_speed: float = 343):
        self.num_mics = num_mics
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate
        self.sound_speed = sound_speed

    def estimate_doa(self, signals: np.ndarray) -> float:
        # Compute time delay between microphones
        cross_correlations = []
        for i in range(1, self.num_mics):
            cross_corr = np.correlate(signals[0], signals[i], mode="full")
            cross_correlations.append(cross_corr)

        # Estimate the time delay by finding the maximum cross-correlation peak
        time_delays = []
        for corr in cross_correlations:
            max_idx = np.argmax(corr) - (len(corr) // 2)
            time_delay = max_idx / self.sample_rate
            time_delays.append(time_delay)

        # Average time delay across all microphone pairs
        avg_time_delay = np.mean(time_delays)

        # Compute angle based on time delay and microphone geometry
        max_delay = self.mic_distance / self.sound_speed
        normalized_delay = np.clip(avg_time_delay / max_delay, -1, 1)
        angle = np.arcsin(normalized_delay) * (180 / np.pi)  # Convert to degrees

        # Ensure angle is in the range [-90°, 90°]
        return angle

    def apply_beamforming(self, signals: np.ndarray, doa_angle: float) -> np.ndarray:
        weights = np.hanning(self.num_mics)
        return np.sum(signals * weights[:, None], axis=0)

    def suppress_noise(self, signal: np.ndarray, noise_type: str) -> np.ndarray:
        noise_type = noise_type.lower()
        noise_profile = NoiseProfiles.profiles.get(noise_type, None)
        if not noise_profile:
            raise ValueError("Unknown noise type")
        # Ensure frequencies and amplitude pattern match
        freqs = np.fft.rfftfreq(len(signal), 1 / self.sample_rate)
        filter_response = np.interp(freqs, noise_profile.frequencies, noise_profile.amplitude_pattern)
        fft_signal = np.fft.rfft(signal)
        filtered_signal = fft_signal * filter_response
        return np.fft.irfft(filtered_signal)

    def process_frame(self, frame: np.ndarray, noise_type: Optional[str] = None) -> Tuple[np.ndarray, float]:
        if frame.shape != (self.num_mics, self.FRAME_SIZE):
            raise ValueError(f"Frame must have shape ({self.num_mics}, {self.FRAME_SIZE})")
        doa = self.estimate_doa(frame)
        enhanced_signal = self.apply_beamforming(frame, doa)
        if noise_type:
            enhanced_signal = self.suppress_noise(enhanced_signal, noise_type)
        return enhanced_signal, doa

    def process_for_model(self, audio: np.ndarray, model_type: str) -> np.ndarray:
        voice_model = VoiceModelInterface(model_type)
        return voice_model.preprocess(audio)


def test_system() -> None:
    num_mics = 4
    mic_distance = 0.05
    sample_rate = 16000
    frame_size = EnhancedAdaptiveBeamformer.FRAME_SIZE

    # Simulated 4-mic array signal
    signals = np.random.randn(num_mics, frame_size) * 0.01

    # Beamformer instance
    beamformer = EnhancedAdaptiveBeamformer(num_mics, mic_distance, sample_rate, sound_speed=343)

    # Test DOA estimation
    doa = beamformer.estimate_doa(signals)
    print(f"Estimated DOA: {doa}°")

    # Test beamforming
    enhanced_signal = beamformer.apply_beamforming(signals, doa)
    print(f"Enhanced signal shape: {enhanced_signal.shape}")

    # Test noise suppression
    noise_type = "tv"
    suppressed_signal = beamformer.suppress_noise(enhanced_signal, noise_type)
    print(f"Noise suppressed signal shape: {suppressed_signal.shape}")

    # Test frame processing
    processed_frame, frame_doa = beamformer.process_frame(signals, noise_type)
    print(f"Processed frame shape: {processed_frame.shape}, DOA: {frame_doa}°")

    # Test model preprocessing
    model_type = "wake_word"
    processed_for_model = beamformer.process_for_model(processed_frame, model_type)
    print(f"Processed for model shape: {processed_for_model.shape}")


# Run tests
test_system()
