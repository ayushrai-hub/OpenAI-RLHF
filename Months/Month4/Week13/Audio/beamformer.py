import numpy as np
from typing import Tuple, Optional

class EnhancedAdaptiveBeamformer:
    def __init__(self, num_mics: int = 4, mic_distance: float = 0.05, 
                 sample_rate: int = 16000, sound_speed: float = 343):
        self.num_mics = num_mics
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate
        self.sound_speed = sound_speed

    def simulate_microphone_signals(self, target_signal: np.ndarray, noise_signal: np.ndarray, doa_angles: list) -> np.ndarray:
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
        n = len(sig1)
        SIG1 = np.fft.fft(sig1)
        SIG2 = np.fft.fft(sig2)
        R = SIG1 * np.conj(SIG2)
        cross_corr = np.fft.ifft(R / np.abs(R))
        max_delay_idx = np.argmax(np.abs(cross_corr))
        
        max_delay = max_delay_idx if max_delay_idx < n // 2 else max_delay_idx - n
        time_delay = max_delay / self.sample_rate
        doa_angle = np.arcsin(time_delay * self.sound_speed / self.mic_distance) * (180 / np.pi)
        
        return doa_angle

    def apply_beamforming(self, signals: np.ndarray, doa_angle: float) -> np.ndarray:
        num_samples = signals.shape[1]
        beamformed_signal = np.zeros(num_samples)
        
        for mic_idx in range(self.num_mics):
            delay = (self.mic_distance * mic_idx * np.cos(np.deg2rad(doa_angle))) / self.sound_speed
            delay_samples = int(delay * self.sample_rate)
            delayed_signal = np.roll(signals[mic_idx], delay_samples)
            beamformed_signal += delayed_signal
        
        beamformed_signal /= self.num_mics
        return beamformed_signal

    def suppress_noise(self, signal: np.ndarray, noise_type: str) -> np.ndarray:
        # Placeholder for noise suppression implementation
        return signal

    def process_frame(self, frame: np.ndarray, noise_type: Optional[str] = None) -> Tuple[np.ndarray, float]:
        signals = self.simulate_microphone_signals(frame, np.random.normal(0, 0.1, len(frame)), [0, 30, 60, 90])
        doa = self.estimate_doa(signals)
        beamformed_signal = self.apply_beamforming(signals, doa)
        if noise_type:
            beamformed_signal = self.suppress_noise(beamformed_signal, noise_type)
        return beamformed_signal, doa

    def process_for_model(self, audio: np.ndarray, model_type: str) -> np.ndarray:
        signals = self.simulate_microphone_signals(audio, np.random.normal(0, 0.1, len(audio)), [0, 30, 60, 90])
        doa = self.estimate_doa(signals)
        beamformed_signal = self.apply_beamforming(signals, doa)
        return beamformed_signal

def test_system() -> None:
    beamformer = EnhancedAdaptiveBeamformer()
    target_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, beamformer.sample_rate, endpoint=False))
    noise_signal = np.random.normal(0, 0.1, len(target_signal))

    # Simulate the process
    signals = beamformer.simulate_microphone_signals(target_signal, noise_signal, [0, 30, 60, 90])
    doa = beamformer.estimate_doa(signals)
    beamformed_signal = beamformer.apply_beamforming(signals, doa)

    assert isinstance(doa, float), "DOA should be a float value"
    assert beamformed_signal.shape == target_signal.shape, "Beamformed signal should have the same shape as input"
