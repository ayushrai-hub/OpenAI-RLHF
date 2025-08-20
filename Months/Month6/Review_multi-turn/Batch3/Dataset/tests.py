import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys

# Mock pywt and alphacsc modules 
sys.modules['pywt'] = MagicMock()
sys.modules['alphacsc'] = MagicMock()
sys.modules['pywt'].cwt = MagicMock(return_value=(np.random.randn(127, 1000), np.random.randn(127, 1000)))
mock_csc_instance = MagicMock()
mock_csc_instance.transform.return_value = [np.random.randn(1000) for _ in range(5)]
sys.modules['alphacsc'].ConvolutionalSparseCoder = MagicMock(return_value=mock_csc_instance)

from ideal_completion import CWTFeatureExtractor, AlphaCSCTransformer  

class TestCWTFeatureExtractor(unittest.TestCase):
    def setUp(self):
        self.scales = np.arange(1, 128)
        self.wavelet = 'morl'
        self.extractor = CWTFeatureExtractor(scales=self.scales, wavelet=self.wavelet)
        self.data = np.random.randn(5, 1000)  # Smaller dataset for testing

    def test_fit_CWT(self):
        # Test the fit method of CWTFeatureExtractor.
        self.assertEqual(self.extractor.fit(self.data), self.extractor)

    def test_transform_CWT(self):
        # Test the transform method of CWTFeatureExtractor.
        features = self.extractor.transform(self.data)
        self.assertEqual(len(features), len(self.data))
        self.assertTrue(all(isinstance(f, np.ndarray) for f in features))

    def test_integration(self):
        # Test the integration of CWTFeatureExtractor and AlphaCSCTransformer.
        csc_transformer = AlphaCSCTransformer(n_atoms=10, atom_length=64, n_iter=10, verbose=False)
        cwt_features = self.extractor.transform(self.data)
        sparse_codes = csc_transformer.fit_transform(cwt_features)
        self.assertEqual(len(sparse_codes), len(self.data))
        self.assertTrue(all(isinstance(code, np.ndarray) for code in sparse_codes))

class TestAlphaCSCTransformer(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(5, 1000)  # Smaller dataset for testing
        self.transformer = AlphaCSCTransformer(n_atoms=10, atom_length=64, n_iter=10, verbose=False)

    def test_fit_AlphaCSC(self):
        # Test the fit method of AlphaCSCTransformer.
        self.assertEqual(self.transformer.fit(self.data), self.transformer)

    @patch('alphacsc.ConvolutionalSparseCoder')
    def test_transform_AlphaCSC(self, MockCSC):
        # Test the transform method of AlphaCSCTransformer.
        MockCSC.return_value = mock_csc_instance
        transformed_data = self.transformer.transform(self.data)
        self.assertEqual(len(transformed_data), len(self.data))
        self.assertTrue(all(isinstance(s, np.ndarray) for s in transformed_data))
        called_args, _ = mock_csc_instance.transform.call_args
        np.testing.assert_array_equal(called_args[0], np.array(self.data))


    @patch('alphacsc.ConvolutionalSparseCoder')
    def test_fit_transform_AlphaCSC(self, MockCSC):

        # Test the fit_transform method of AlphaCSCTransformer.
        MockCSC.return_value = mock_csc_instance
        transformed_data = self.transformer.fit_transform(self.data)
        self.assertEqual(len(transformed_data), len(self.data))
        self.assertTrue(all(isinstance(s, np.ndarray) for s in transformed_data))
        called_args, _ = mock_csc_instance.fit.call_args
        np.testing.assert_array_equal(called_args[0], np.array(self.data))

if __name__ == "__main__":
    unittest.main(verbosity=2)
