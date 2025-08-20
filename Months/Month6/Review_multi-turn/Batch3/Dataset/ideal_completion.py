import numpy as np
import pywt
from alphacsc import ConvolutionalSparseCoder

class CWTFeatureExtractor:
    def __init__(self, scales, wavelet='morl', downsampling_factor=1000, downsampling_scales=None):
        """
        Initialize the CWTFeatureExtractor.
        
        Parameters:
        - scales: List or array of scales for the CWT.
        - wavelet: Wavelet type to use in CWT.
        - downsampling_factor: Integer factor by which to downsample lower scales.
        - downsampling_scales: Scales at which downsampling is applied. If None, defaults to the lower half scales.
        """
        self.scales = scales
        self.wavelet = wavelet
        self.downsampling_factor = downsampling_factor
        if downsampling_scales is None:
            mid_idx = len(scales) // 2
            self.downsampling_scales = scales[:mid_idx]
            self.non_downsampling_scales = scales[mid_idx:]
        else:
            self.downsampling_scales = downsampling_scales
            self.non_downsampling_scales = [scale for scale in scales if scale not in downsampling_scales]

    def fit(self, X, y=None):
        """
        No fitting required for CWT.
        """
        return self

    def transform(self, X):
        """
        Apply CWT to each sample in X, downsampling lower scales and preserving higher scales.
        
        Parameters:
        - X: Array of shape (n_samples, n_timesteps) containing the time series data.
        
        Returns:
        - transformed_features: Array of transformed features for each sample.
        """
        transformed_features = []
        for sample in X:
            # Compute CWT coefficients
            coefficients, _ = pywt.cwt(sample, self.scales, self.wavelet)
            
            downsampled_coeffs = []
            for idx, scale in enumerate(self.scales):
                coeff = coefficients[idx]
                if scale in self.downsampling_scales:
                    # Apply strided downsampling for lower scales
                    downsampled = coeff[::self.downsampling_factor]
                    downsampled_coeffs.append(downsampled)
                else:
                    # Preserve higher-scale coefficients
                    downsampled_coeffs.append(coeff)
            
            # Concatenate downsampled coefficients across scales
            feature_vector = np.concatenate(downsampled_coeffs)
            transformed_features.append(feature_vector)
        
        return np.array(transformed_features)


class AlphaCSCTransformer:
    def __init__(self, n_atoms=10, atom_length=50, n_iter=100, random_state=None, verbose=False):
        """
        Initialize the AlphaCSCTransformer.
        
        Parameters:
        - n_atoms: Number of convolutional atoms to learn.
        - atom_length: Length of each convolutional atom.
        - n_iter: Number of iterations for training.
        - random_state: Random seed for reproducibility.
        - verbose: Controls verbosity during fitting and transformation.
        """
        self.n_atoms = n_atoms
        self.atom_length = atom_length
        self.n_iter = n_iter
        self.random_state = random_state
        self.verbose = verbose
        self.model = ConvolutionalSparseCoder(
            n_atoms=self.n_atoms,
            atom_length=self.atom_length,
            n_iter=self.n_iter,
            rank1=False,  # Linear and equivariant operations only
            uv_constraint=None,  # No constraint to maintain linearity
            random_state=self.random_state,
            verbose=self.verbose
        )

    def fit(self, X, y=None):
        """
        Fit the convolutional sparse coding model to the input data X.
        
        Parameters:
        - X: Array of shape (n_samples, n_timesteps) containing the time series data.
        """
        self.model.fit(X)
        return self

    def transform(self, X):
        """
        Transform data X using the trained sparse coding model, returning sparse codes.
        
        Parameters:
        - X: Array of shape (n_samples, n_timesteps) containing the time series data.
        
        Returns:
        - sparse_codes: Array of sparse codes representing each sample.
        """
        sparse_codes = self.model.transform(X)
        return sparse_codes

    def fit_transform(self, X, y=None):
        """
        Fit the convolutional sparse coding model to the input data X and return the transformed sparse codes.
        
        Parameters:
        - X: Array of shape (n_samples, n_timesteps) containing the time series data.
        
        Returns:
        - sparse_codes: Array of sparse codes representing each sample.
        """
        self.fit(X, y)
        return self.transform(X)
