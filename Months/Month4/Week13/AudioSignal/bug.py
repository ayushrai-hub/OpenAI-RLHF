import numpy as np

# Constants
SAMPLE_RATE = 16000  # Sampling rate in Hz
SOUND_SPEED = 343    # Sound speed in m/s
MIC_DISTANCE = 0.05  # Distance between microphones in meters
NUM_MICS = 4         # Total microphones in the array

# Simulate microphone array signals
def simulate_microphone_signals(target_signal, noise_signal, doa_angles):
    """
    Generate microphone signals given a target signal, a noise signal, and specified DOA angles.
    """
    mic_signals = np.zeros((NUM_MICS, len(target_signal)))
    for i in range(NUM_MICS):
        delay = (MIC_DISTANCE * i * np.cos(np.deg2rad(doa_angles[i]))) / SOUND_SPEED
        delay_samples = int(delay * SAMPLE_RATE)
        mic_signals[i, delay_samples:delay_samples+len(target_signal)] += target_signal
        mic_signals[i, :len(noise_signal)] += noise_signal
    return mic_signals

# Simple DOA estimation using GCC-PHAT
def estimate_doa(signals):
    """
    DOA estimation based on received microphone signals.
    """
    # For simplicity, employ cross-correlation between the first two microphones
    sig1 = signals[0]
    sig2 = signals[1]
    n = len(sig1)
    SIG1 = np.fft.fft(sig1)
    SIG2 = np.fft.fft(sig2)
    R = SIG1 * np.conj(SIG2)
    cross_corr = np.fft.ifft(R / np.abs(R))
    max_delay_idx = np.argmax(np.abs(cross_corr))
    
    # Convert delay to angle (assuming far-field approximation)
    max_delay = max_delay_idx if max_delay_idx < n // 2 else max_delay_idx - n
    time_delay = max_delay / SAMPLE_RATE
    doa_angle = np.arcsin(time_delay * SOUND_SPEED / MIC_DISTANCE) * (180 / np.pi)
    
    return doa_angle

# Delay-and-sum beamformer
def delay_and_sum(signals, doa_angle):
    """
    Simple delay-and-sum beamformer.
    """
    num_samples = signals.shape[1]
    beamformed_signal = np.zeros(num_samples)
    
    for mic_idx in range(NUM_MICS):
        # Calculate the delay based on the estimated DOA angle
        delay = (MIC_DISTANCE * mic_idx * np.cos(np.deg2rad(doa_angle))) / SOUND_SPEED
        delay_samples = int(delay * SAMPLE_RATE)
        
        # Delay the microphone signal accordingly
        delayed_signal = np.roll(signals[mic_idx], delay_samples)
        
        # Sum all delayed signals
        beamformed_signal += delayed_signal
    
    # Normalize the beamformed signal by the number of microphones
    beamformed_signal /= NUM_MICS
    
    return beamformed_signal

# Example usage
if __name__ == "__main__":
    # Simulate a target signal (speech) and noise
    t = np.linspace(0, 1, SAMPLE_RATE, endpoint=False)
    target_signal = np.sin(2 * np.pi * 440 * t)  # Simulated speech at 440Hz
    noise_signal = np.random.normal(0, 0.1, len(t))  # Simulated noise

    # Simulate microphone signals with different DOA angles
    doa_angles = [0, 30, 60, 90]  # DOA angles in degrees for each mic
    mic_signals = simulate_microphone_signals(target_signal, noise_signal, doa_angles)

    # Estimate DOA
    estimated_doa = estimate_doa(mic_signals)
    print(f"Estimated DOA: {estimated_doa:.2f} degrees")

    # Perform delay-and-sum beamforming
    beamformed_signal = delay_and_sum(mic_signals, estimated_doa)

    # Play or save the beamformed signal for evaluation
    # You can use an audio library like sounddevice or scipy.io.wavfile to play/save
    # For example:
    # import sounddevice as sd
    # sd.play(beamformed_signal, SAMPLE_RATE)
