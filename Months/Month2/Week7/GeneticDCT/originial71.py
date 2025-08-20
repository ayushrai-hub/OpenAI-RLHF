import numpy as np
from scipy.fftpack import idct

def dct_to_pixel(dct_coeffs, quantization_table, original_shape):
    """
    Convert DCT coefficients back to pixel values.
    
    Args:
    dct_coeffs (np.ndarray): DCT coefficients, shape (height, width)
    quantization_table (np.ndarray): Quantization table, shape (8, 8)
    original_shape (tuple): Original image shape (height, width)
    
    Returns:
    np.ndarray: Reconstructed image, shape original_shape
    """
    height, width = original_shape
    blocks_height, blocks_width = height // 8, width // 8
    
    # Validate input shapes
    if dct_coeffs.shape != original_shape or quantization_table.shape != (8, 8):
        raise ValueError("Invalid input shapes")
    
    # Reshape to 8x8 blocks
    dct_blocks = dct_coeffs.reshape(blocks_height, blocks_width, 8, 8)
    
    # Dequantize the coefficients
    dequantized_blocks = dct_blocks * quantization_table[np.newaxis, np.newaxis, :, :]
    
    # Perform inverse DCT (iDCT) on each block
    idct_blocks = np.zeros_like(dequantized_blocks)
    for i in range(blocks_height):
        for j in range(blocks_width):
            idct_blocks[i, j] = idct(idct(dequantized_blocks[i, j], axis=1, norm='ortho'), axis=0, norm='ortho')
    
    # Rearrange the blocks back into the full image
    idct_image = idct_blocks.transpose(0, 2, 1, 3).reshape(height, width)
    
    return idct_image

