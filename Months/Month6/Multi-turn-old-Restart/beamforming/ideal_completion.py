import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

class Int24:
    MAX_VALUE: int = 8388607  # 2^23 - 1
    MIN_VALUE: int = -8388608  # -2^23

    @staticmethod
    def clip(value: np.ndarray) -> np.ndarray:
        return np.clip(value, Int24.MIN_VALUE, Int24.MAX_VALUE)

    @staticmethod
    def to_int24(float_val: np.ndarray) -> np.ndarray:
        int_val = np.round(float_val).astype(np.int32)
        return Int24.clip(int_val)

    @staticmethod
    def from_int24(int24_val: np.ndarray) -> np.ndarray:
        return int24_val.astype(np.float32)

@dataclass
class NoiseProfile:
    type: str
    frequency_range: Tuple[float, float]
    amplitude_pattern: np.ndarray

class NoiseProfiles:
    TV_SOUND = NoiseProfile(
        type="TV",
        frequency_range=(300, 3400),
        amplitude_pattern=np.array([0.8, 1.0, 0.9])
    )
    VACUUM = NoiseProfile(
        type="Vacuum",
        frequency_range=(100, 1000),
        amplitude_pattern=np.array([1.0, 0.7, 0.5])
    )
    KITCHEN = NoiseProfile(
        type="Kitchen",
        frequency_range=(50, 2000),
        amplitude_pattern=np.array([0.6, 0.8, 1.0])
    )

class EmbeddedDNN:
    def __init__(self, input_size: int = 1024, hidden_size: int = 64):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.weights1 = np.random.randn(self.input_size, self.hidden_size) * 0.01
        self.weights2 = np.random.randn(self.hidden_size, 1) * 0.01
        self.bias1 = np.zeros(self.hidden_size)
        self.bias2 = np.zeros(1)

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    def forward(self, x: np.ndarray) -> np.ndarray:
        z1 = x.dot(self.weights1) + self.bias1
        a1 = self.relu(z1)
        z2 = a1.dot(self.weights2) + self.bias2
        output = self.sigmoid(z2)
        return output

class VoiceModelInterface:
    VALID_MODEL_TYPES = {"wake_word", "local_command", "cloud"}

    def __init__(self, model_type: str):
        if model_type not in self.VALID_MODEL_TYPES:
            raise ValueError(f"Unknown model type: {model_type}")
        self.model_type = model_type

    def preprocess(self, audio: np.ndarray) -> np.ndarray:
        if self.model_type == "wake_word":
            return self._preprocess_wake_word(audio)
        elif self.model_type == "local_command":
            return self._preprocess_local_command(audio)
        elif self.model_type == "cloud":
            return self._preprocess_cloud(audio)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def _preprocess_wake_word(self, audio: np.ndarray) -> np.ndarray:
        max_val = np.max(np.abs(audio))
        if max_val == 0:
            return audio
        return audio / max_val

    def _preprocess_local_command(self, audio: np.ndarray) -> np.ndarray:
        std_dev = np.std(audio)
        if std_dev == 0:
            return audio - np.mean(audio)
        return (audio - np.mean(audio)) / (std_dev + 1e-5)

    def _preprocess_cloud(self, audio: np.ndarray) -> np.ndarray:
        return audio / 32768.0

class EnhancedAdaptiveBeamformer:
    FRAME_SIZE = 1024  # 64ms frame size at 16kHz

    def __init__(self, num_mics: int = 4, mic_distance: float = 0.05, 
                 sample_rate: int = 16000, sound_speed: float = 343):
        self.num_mics = num_mics
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate
        self.sound_speed = sound_speed

    def estimate_doa(self, signals: np.ndarray) -> float:
        if signals.shape[0] != self.num_mics:
            raise ValueError(f"Expected {self.num_mics} microphone signals, got {signals.shape[0]}")
        correlation = np.correlate(signals[0], signals[1], "full")
        delay_idx = np.argmax(np.abs(correlation)) - (len(signals[0]) - 1)
        time_delay = delay_idx / self.sample_rate
        sin_theta = time_delay * self.sound_speed / self.mic_distance
        sin_theta = np.clip(sin_theta, -1.0, 1.0)  # Ensure within valid range for arcsin
        angle = np.arcsin(sin_theta)
        angle_degrees = np.degrees(angle)
        angle_degrees = np.clip(angle_degrees, -90, 90)  # Ensure angle is between -90 and 90
        return angle_degrees

    def apply_beamforming(self, signals: np.ndarray, doa_angle: float) -> np.ndarray:
        if signals.shape[0] != self.num_mics:
            raise ValueError(f"Expected {self.num_mics} microphone signals, got {signals.shape[0]}")
        if signals.shape[1] != self.FRAME_SIZE:
            raise ValueError(f"Expected frame size of {self.FRAME_SIZE}, got {signals.shape[1]}")
        doa_radians = np.radians(doa_angle)
        delays = np.array([i * self.mic_distance * np.sin(doa_radians) / self.sound_speed 
                           for i in range(self.num_mics)])
        delayed_signals = np.zeros(self.FRAME_SIZE)
        for i in range(self.num_mics):
            delay_samples = int(np.round(delays[i] * self.sample_rate))
            if delay_samples > 0:
                delayed_signals[delay_samples:] += signals[i][:-delay_samples]
            elif delay_samples < 0:
                delayed_signals[:delay_samples] += signals[i][-delay_samples:]
            else:
                delayed_signals += signals[i]
        return delayed_signals / self.num_mics

    def suppress_noise(self, signal: np.ndarray, noise_type: str) -> np.ndarray:
        if signal.shape[0] != self.FRAME_SIZE:
            raise ValueError(f"Expected signal frame size of {self.FRAME_SIZE}, got {signal.shape[0]}")
        noise_type = noise_type.lower()
        if noise_type == "tv":
            noise_profile = NoiseProfiles.TV_SOUND
        elif noise_type == "vacuum":
            noise_profile = NoiseProfiles.VACUUM
        elif noise_type == "kitchen":
            noise_profile = NoiseProfiles.KITCHEN
        else:
            raise ValueError(f"Unknown noise type: {noise_type}")

        # Simplified noise suppression by applying a basic filter
        freq_signal = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), d=1/self.sample_rate)
        filter_mask = np.logical_and(freqs >= noise_profile.frequency_range[0], freqs <= noise_profile.frequency_range[1])
        suppression_factor = 1 - noise_profile.amplitude_pattern.mean()
        freq_signal[filter_mask] *= suppression_factor
        return np.fft.irfft(freq_signal, n=len(signal))

    def process_frame(self, frame: np.ndarray, noise_type: Optional[str] = None) -> Tuple[np.ndarray, float]:
        if frame.shape != (self.num_mics, self.FRAME_SIZE):
            raise ValueError(f"Frame must be of shape ({self.num_mics}, {self.FRAME_SIZE}), got {frame.shape}")
        doa_angle = self.estimate_doa(frame)
        beamformed_signal = self.apply_beamforming(frame, doa_angle)
        if noise_type:
            beamformed_signal = self.suppress_noise(beamformed_signal, noise_type)
        return beamformed_signal, doa_angle

    def process_for_model(self, audio: np.ndarray, model_type: str) -> np.ndarray:
        if audio.shape[0] != self.FRAME_SIZE:
            raise ValueError(f"Expected audio length of {self.FRAME_SIZE}, got {audio.shape[0]}")
        interface = VoiceModelInterface(model_type)
        return interface.preprocess(audio)

def test_system() -> None:
    # Create dummy multi-channel signals (4 microphones)
    np.random.seed(0)  # For reproducibility
    num_mics = 4
    sample_rate = 16000
    frame_size = EnhancedAdaptiveBeamformer.FRAME_SIZE
    t = np.linspace(0, frame_size / sample_rate, frame_size, endpoint=False)
    freq = 1000  # 1kHz test tone
    signals = np.array([np.sin(2 * np.pi * freq * t + np.random.rand()) for _ in range(num_mics)])
    
    beamformer = EnhancedAdaptiveBeamformer(num_mics=num_mics, mic_distance=0.05, sample_rate=sample_rate)
    processed_signal, doa_angle = beamformer.process_frame(signals, noise_type="TV")
    print(f"Estimated DOA Angle: {doa_angle}")
    print(f"Processed Signal (first 10 samples): {processed_signal[:10]}")
    
    model_audio = beamformer.process_for_model(processed_signal, model_type="wake_word")
    print(f"Model Audio (first 10 samples): {model_audio[:10]}")

    # Testing Int24 conversion
    float_signal = np.random.uniform(-1.0, 1.0, frame_size) * Int24.MAX_VALUE
    int24_signal = Int24.to_int24(float_signal)
    recovered_float_signal = Int24.from_int24(int24_signal)
    print(f"Original Float Signal (first 10 samples): {float_signal[:10]}")
    print(f"Int24 Signal (first 10 samples): {int24_signal[:10]}")
    print(f"Recovered Float Signal (first 10 samples): {recovered_float_signal[:10]}")

if __name__ == "__main__":
    test_system()