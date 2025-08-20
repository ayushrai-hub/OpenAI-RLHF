import unittest
import numpy as np
from scipy.fftpack import dct, idct
from original import dct_to_pixel
class TestDCTToPixel(unittest.TestCase):
    def setUp(self):
        self.original_shape = (16, 16)
        self.quantization_table = np.ones((8, 8))

    def test_output_shape(self):
        dct_coeffs = np.random.rand(16, 16)
        result = dct_to_pixel(dct_coeffs, self.quantization_table, self.original_shape)
        self.assertEqual(result.shape, self.original_shape)

    def test_identity_transformation(self):
        original_image = np.random.rand(16, 16)
        dct_coeffs = dct(dct(original_image.T, norm='ortho').T, norm='ortho')
        result = dct_to_pixel(dct_coeffs, self.quantization_table, self.original_shape)
        np.testing.assert_allclose(result, original_image, atol=1e-6)

    def test_zero_input(self):
        dct_coeffs = np.zeros((16, 16))
        result = dct_to_pixel(dct_coeffs, self.quantization_table, self.original_shape)
        np.testing.assert_allclose(result, np.zeros((16, 16)), atol=1e-6)

    def test_custom_quantization(self):
        dct_coeffs = np.random.rand(16, 16)
        custom_quant = np.random.rand(8, 8) + 0.5
        result = dct_to_pixel(dct_coeffs, custom_quant, self.original_shape)
        self.assertEqual(result.shape, self.original_shape)

    def test_large_image(self):
        large_shape = (256, 256)
        dct_coeffs = np.random.rand(*large_shape)
        result = dct_to_pixel(dct_coeffs, self.quantization_table, large_shape)
        self.assertEqual(result.shape, large_shape)

if __name__ == '__main__':
    unittest.main(verbosity=2)