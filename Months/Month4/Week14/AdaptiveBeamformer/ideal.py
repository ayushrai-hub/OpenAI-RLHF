# ideal_completion.py

import numpy as np
from scipy import signal
from scipy.signal import windows
import time
import sys

class AdaptiveBeamformer:
    def __init__(self, 
                 num_mics: int = 4,
                 mic_distance: float = 0.05,
                 sample_rate: int = 16000,
                 sound_speed: float = 343,
                 use_subband: bool = True,
                 num_bands: int = 8):
        """
        Initialize the adaptive beamformer with configurable parameters.
        Supports both fullband and subband processing.
        """
        self.num_mics = num_mics
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate
        self.sound_speed = sound_speed
        self.use_subband = use_subband
        self.num_bands = num_bands
        
        # Initialize subband processing if enabled
        if self.use_subband:
            # Use shorter window length to prevent excessive padding
            self.analysis_window = signal.firwin(num_bands * 2, 1.0 / num_bands)
            
        # Rest of the initialization remains the same
        self.noise_profiles = {
            'tv': {'freq_range': (100, 4000), 'threshold': 0.3},
            'vacuum': {'freq_range': (50, 1000), 'threshold': 0.5},
            'kitchen': {'freq_range': (200, 3000), 'threshold': 0.4}
        }

        self.wake_word_params = {
            'freq_range': (500, 3000),
            'duration': int(0.5 * sample_rate),
            'energy_threshold': 0.7,
            'detection_window': 1024
        }

        self.buffer_size = 512
        self.overlap = 256
        self.history_buffer = np.zeros((num_mics, self.buffer_size * 2))
        self.processing_latency = []
        self.max_memory = 1024 * 1024
        self.current_memory = 0
        self.buffer_pool = []
        self.memory_usage_history = []
        self.metrics_history = {
            'snr': [],
            'latency': [],
            'memory_usage': [],
            'wake_word_detections': [],
            'noise_classifications': []
        }
        
    def to_fixed_point(self, data: np.ndarray, scale: float = 2**23-1) -> np.ndarray:
        return np.clip(np.round(data * scale), -scale, scale-1).astype(np.int32)
        
    def from_fixed_point(self, data: np.ndarray, scale: float = 2**23-1) -> np.ndarray:
        return data.astype(np.float32) / scale

    def subband_decomposition(self, signal_data: np.ndarray) -> np.ndarray:
        """
        Decompose signal into subbands using polyphase filterbank.
        Returns subbands of equal length.
        """
        # Ensure signal length is multiple of num_bands
        pad_length = (self.num_bands - (len(signal_data) % self.num_bands)) % self.num_bands
        padded_signal = np.pad(signal_data, (0, pad_length), 'constant')
        
        # Reshape into subbands
        subbands = padded_signal.reshape(-1, self.num_bands).T
        
        # Apply filtering to each subband
        filtered_subbands = np.zeros_like(subbands)
        for i in range(self.num_bands):
            filtered_subbands[i] = signal.convolve(
                subbands[i], 
                self.analysis_window, 
                mode='same'
            )
        
        return filtered_subbands

    def detect_wake_word(self, signal: np.ndarray) -> bool:
        fft_signal = np.fft.fft(signal)
        freq_bins = np.fft.fftfreq(len(signal), 1/self.sample_rate)
        mask = (freq_bins >= self.wake_word_params['freq_range'][0]) & \
               (freq_bins <= self.wake_word_params['freq_range'][1])
        
        wake_word_energy = np.sum(np.abs(fft_signal[mask])**2)
        total_energy = np.sum(np.abs(fft_signal)**2)
        
        return wake_word_energy / total_energy > self.wake_word_params['energy_threshold']
        
    def estimate_doa(self, signals: np.ndarray) -> float:
        """
        Enhanced DOA estimation using GCC-PHAT across all microphone pairs
        """
        start_time = time.time()
        doa_estimates = []
        
        # Add voice activity detection
        energy = np.mean(signals**2, axis=1)
        if np.max(energy) < 1e-6:  # If no significant activity
            return 0.0
            
        # Process each microphone pair
        for i in range(self.num_mics-1):
            for j in range(i+1, self.num_mics):
                sig1 = signals[i]
                sig2 = signals[j]
                
                # Memory optimization - reuse buffers from pool
                if len(self.buffer_pool) > 0:
                    sig1_fixed = self.buffer_pool.pop()
                    sig2_fixed = self.buffer_pool.pop()
                else:
                    sig1_fixed = np.zeros_like(sig1)
                    sig2_fixed = np.zeros_like(sig2)
                
                # Convert to fixed point for embedded processing
                sig1_fixed = self.to_fixed_point(sig1)
                sig2_fixed = self.to_fixed_point(sig2)
                
                # GCC-PHAT with noise robustness
                SIG1 = np.fft.fft(self.from_fixed_point(sig1_fixed))
                SIG2 = np.fft.fft(self.from_fixed_point(sig2_fixed))
                R = SIG1 * np.conj(SIG2)
                
                # Add noise robustness
                noise_floor = np.median(np.abs(R)) * 2
                R[np.abs(R) < noise_floor] = 0
                
                gcc = np.fft.ifft(R / (np.abs(R) + 1e-10))
                
                # Find peak with confidence measure
                max_idx = np.argmax(np.abs(gcc))
                peak_val = np.abs(gcc[max_idx])
                if peak_val > 0.5:  # Only consider reliable peaks
                    n = len(gcc)
                    delay_idx = max_idx if max_idx < n//2 else max_idx - n
                    
                    # Convert to angle
                    time_delay = delay_idx / self.sample_rate
                    pair_distance = self.mic_distance * abs(j-i)
                    doa = np.arcsin(np.clip(time_delay * self.sound_speed / pair_distance, -1, 1))
                    doa_estimates.append(np.rad2deg(doa))
                
                # Return buffers to pool
                self.buffer_pool.extend([sig1_fixed, sig2_fixed])
                
        # Update latency metrics
        self.processing_latency.append(time.time() - start_time)
        
        # Return median DOA estimate
        return np.median(doa_estimates) if doa_estimates else 0.0

    def adaptive_weights(self, signals: np.ndarray, doa: float) -> np.ndarray:
        """
        Calculate adaptive weights using MVDR principle with noise handling
        """
        start_time = time.time()
        
        # Calculate signal features for adaptive processing
        signal_power = np.mean(np.abs(signals)**2, axis=1)
        signal_features = np.concatenate([signal_power, np.diff(signal_power)])
        
        # Combine with traditional MVDR weights
        R = np.zeros((self.num_mics, self.num_mics), dtype=np.complex64)
        
        # Estimate spatial correlation matrix with noise consideration
        for i in range(self.num_mics):
            for j in range(self.num_mics):
                R[i,j] = np.mean(signals[i] * np.conj(signals[j]))
        
        # Apply spectral subtraction for common noise types
        freq_response = np.fft.fft(signals, axis=1)
        
        # Simple noise classification based on spectral characteristics
        noise_type = 'tv'  # Default noise type
        for noise_type, profile in self.noise_profiles.items():
            freq_start = int(profile['freq_range'][0] * len(freq_response[0]) / self.sample_rate)
            freq_end = int(profile['freq_range'][1] * len(freq_response[0]) / self.sample_rate)
            energy_in_band = np.sum(np.abs(freq_response[:, freq_start:freq_end])**2)
            if energy_in_band > 0.5 * np.sum(np.abs(freq_response)**2):
                break
                
        # Apply noise profile
        profile = self.noise_profiles[noise_type]
        freq_start = int(profile['freq_range'][0] * len(freq_response[0]) / self.sample_rate)
        freq_end = int(profile['freq_range'][1] * len(freq_response[0]) / self.sample_rate)
        freq_response[:, freq_start:freq_end] *= (1 - profile['threshold'])
        
        signals = np.real(np.fft.ifft(freq_response, axis=1))
                   
        # Steering vector with wake word optimization
        d = np.exp(-1j * 2 * np.pi * self.mic_distance * 
                   np.arange(self.num_mics) * np.cos(np.deg2rad(doa)))
                   
        # MVDR weights with stability enhancement
        try:
            # Add diagonal loading for stability
            R += 1e-3 * np.trace(R) / len(R) * np.eye(self.num_mics)
            R_inv = np.linalg.inv(R)
            w = R_inv @ d
            w = w / (d.conj() @ R_inv @ d)
            
            # Apply adaptive scaling based on signal features
            w *= (1 + 0.1 * signal_features)[:, np.newaxis]
        except:
            w = np.ones(self.num_mics) / self.num_mics
        
        # Update performance metrics
        self.metrics_history['latency'].append(time.time() - start_time)
        self.current_memory = sum(sys.getsizeof(arr) for arr in [R, w, signals])
        self.metrics_history['memory_usage'].append(self.current_memory)
            
        return self.to_fixed_point(w)

    def process(self, signals: np.ndarray) -> np.ndarray:
        """
        Main processing pipeline with fixed subband decomposition
        """
        start_time = time.time()
        frame_start = 0
        processed_frames = []
        
        while frame_start + self.buffer_size <= signals.shape[1]:
            frame = signals[:, frame_start:frame_start + self.buffer_size]
            
            if self.use_subband:
                # Process each microphone signal
                subbands = [self.subband_decomposition(sig) for sig in frame]
                processed_subbands = np.zeros((self.num_bands, self.buffer_size // self.num_bands))
                
                for band_idx in range(self.num_bands):
                    # Extract the current subband signals for all microphones
                    band_signals = np.array([sb[band_idx] for sb in subbands])
                    
                    # Process each subband
                    doa = self.estimate_doa(band_signals)
                    weights = self.adaptive_weights(band_signals, doa)
                    
                    processed_band = np.sum(
                        self.from_fixed_point(weights)[:, np.newaxis] * band_signals, 
                        axis=0
                    )
                    
                    if self.detect_wake_word(processed_band):
                        self.metrics_history['wake_word_detections'].append(time.time())
                        freq_response = np.fft.fft(processed_band)
                        freq_bins = np.fft.fftfreq(len(processed_band), 1/self.sample_rate)
                        wake_mask = (freq_bins >= self.wake_word_params['freq_range'][0]) & \
                                  (freq_bins <= self.wake_word_params['freq_range'][1])
                        freq_response[wake_mask] *= 1.5
                        processed_band = np.real(np.fft.ifft(freq_response))
                    
                    if band_idx < self.num_bands // 2:
                        processed_band *= 0.8
                        
                    processed_subbands[band_idx] = processed_band
                
                # Reconstruct the frame from subbands
                processed_frame = np.zeros(self.buffer_size)
                subband_length = self.buffer_size // self.num_bands
                for i in range(self.num_bands):
                    processed_frame[i::self.num_bands] = processed_subbands[i]
                
            else:
                # Fullband processing
                doa = self.estimate_doa(frame)
                weights = self.adaptive_weights(frame, doa)
                processed_frame = np.sum(
                    self.from_fixed_point(weights)[:, np.newaxis] * frame, 
                    axis=0
                )
            
            processed_frames.append(processed_frame)
            frame_start += self.overlap
            
            self.current_memory = sum(sys.getsizeof(arr) for arr in 
                                    [processed_frames, frame, weights])
            if self.current_memory > self.max_memory:
                self.buffer_pool = []
            
            self.metrics_history['latency'].append(time.time() - start_time)
            self.metrics_history['memory_usage'].append(self.current_memory)
        
        # Overlap-add reconstruction
        output_signal = np.zeros(signals.shape[1])
        frame_start = 0
        window = windows.hann(self.buffer_size)  # Apply windowing for smooth reconstruction
        
        for frame in processed_frames:
            output_signal[frame_start:frame_start + self.buffer_size] += frame * window
            frame_start += self.overlap
            
        return output_signal

    def evaluate_performance(self, 
                           clean_signal: np.ndarray, 
                           processed_signal: np.ndarray) -> dict:
        """
        Calculate comprehensive performance metrics including real-time monitoring
        """
        # Handle different lengths if necessary
        min_length = min(len(clean_signal), len(processed_signal))
        clean_signal = clean_signal[:min_length]
        processed_signal = processed_signal[:min_length]
        
        # Basic metrics
        noise_est = processed_signal - clean_signal
        snr = 10 * np.log10(
            np.sum(clean_signal**2) / (np.sum(noise_est**2) + 1e-10)
        )
        
        # Speech-specific metrics
        def envelope(x):
            return np.abs(signal.hilbert(x))
        
        env_corr = np.corrcoef(envelope(clean_signal), envelope(processed_signal))[0,1]
        
        # Speech clarity metric
        clarity = np.sum(np.abs(processed_signal)) / (np.sum(np.abs(noise_est)) + 1e-10)
        
        # Compute PESQ-like metric (simplified version for embedded systems)
        def compute_pesq_like():
            # Frame the signals
            frame_length = 256
            clean_frames = np.array([clean_signal[i:i+frame_length] 
                                   for i in range(0, len(clean_signal)-frame_length, frame_length)])
            proc_frames = np.array([processed_signal[i:i+frame_length] 
                                  for i in range(0, len(processed_signal)-frame_length, frame_length)])
            
            # Compute frame-wise correlation
            correlations = np.array([np.corrcoef(c, p)[0,1] if len(c) == len(p) else 0
                                   for c, p in zip(clean_frames, proc_frames)])
            
            # Convert to PESQ-like scale (1-5)
            return 1 + 4 * np.mean(correlations)
        
        # Compute STOI-like metric (simplified for embedded systems)
        def compute_stoi_like():
            # Compute short-time correlation in frequency domain
            nfft = 512
            clean_spec = np.abs(np.fft.fft(clean_signal, nfft))
            proc_spec = np.abs(np.fft.fft(processed_signal, nfft))
            
            # Normalize and compute correlation
            clean_spec_norm = clean_spec / (np.sum(clean_spec) + 1e-10)
            proc_spec_norm = proc_spec / (np.sum(proc_spec) + 1e-10)
            
            return np.sum(np.minimum(clean_spec_norm, proc_spec_norm))
        
        # Real-time performance metrics
        latency_stats = {
            'mean': np.mean(self.metrics_history['latency']),
            'max': np.max(self.metrics_history['latency']),
            'std': np.std(self.metrics_history['latency'])
        }
        
        # Memory usage statistics
        memory_stats = {
            'current': self.current_memory,
            'peak': np.max(self.metrics_history['memory_usage']),
            'average': np.mean(self.metrics_history['memory_usage'])
        }
        
        # Wake word detection statistics
        if len(self.metrics_history['wake_word_detections']) > 0:
            wake_word_latency = np.diff(self.metrics_history['wake_word_detections'])
            wake_word_stats = {
                'count': len(self.metrics_history['wake_word_detections']),
                'avg_interval': np.mean(wake_word_latency) if len(wake_word_latency) > 0 else 0
            }
        else:
            wake_word_stats = {'count': 0, 'avg_interval': 0}
        
        # Calculate buffer efficiency
        buffer_stats = {
            'pool_size': len(self.buffer_pool),
            'memory_efficiency': 1 - (self.current_memory / self.max_memory)
        }
        
        # Comprehensive performance metrics dictionary
        return {
            # Audio quality metrics
            'SNR': snr,
            'MSE': np.mean((clean_signal - processed_signal)**2),
            'Speech_Clarity': clarity,
            'Envelope_Correlation': env_corr,
            'PESQ_like': compute_pesq_like(),
            'STOI_like': compute_stoi_like(),
            
            # Real-time performance
            'Latency': latency_stats,
            'Memory_Usage': memory_stats,
            'Wake_Word_Stats': wake_word_stats,
            'Buffer_Stats': buffer_stats,
            
            # System health
            'Processing_Stability': 1.0 if all(l < 0.1 for l in self.metrics_history['latency'][-100:]) else 0.0,
            'Memory_Stability': 1.0 if memory_stats['peak'] < self.max_memory * 0.9 else 0.0
        }

