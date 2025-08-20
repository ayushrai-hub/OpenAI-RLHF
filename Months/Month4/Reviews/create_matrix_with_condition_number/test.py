import unittest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
from ideal_completion import create_matrix_with_condition_number, main

class TestCreateMatrixWithConditionNumber(unittest.TestCase):
    
    # Test 1: Check zero condition number handling
    def test_zero_condition_number(self):
        """Test that a zero condition number returns None instead of raising an error."""
        # Purpose: Ensure the function returns None when given a zero condition number.
        # Verifying: The function does not raise an error on invalid input, like cond_num=0.
        # Importance: Zero condition numbers are invalid, and graceful handling prevents crashes.
        result = create_matrix_with_condition_number(dimension=3, cond_num=0)
        self.assertIsNone(result, "Expected None for zero condition number")

    # Test 2: Check non-integer dimension handling
    def test_non_integer_dimension(self):
        """Test that a non-integer dimension returns None instead of raising an error."""
        # Purpose: Check that passing a non-integer dimension (like 3.5) returns None.
        # Verifying: The function rejects non-integer dimensions to avoid undefined behavior.
        # Importance: Dimensions of matrices must be integers, so this ensures robust input validation.
        result = create_matrix_with_condition_number(dimension=3.5, cond_num=10)
        self.assertIsNone(result, "Expected None for non-integer dimension")

    # Test 3: Check correct matrix creation with valid inputs
    def test_valid_matrix_creation(self):
        """Test that a valid matrix is created with the specified condition number."""
        # Purpose: Confirm that a matrix is correctly created when inputs are valid.
        # Verifying: Matrix creation, shape, and condition number accuracy.
        # Importance: Ensures the function works correctly when given valid, expected inputs.
        dimension = 3
        cond_num = 10
        matrix_A = create_matrix_with_condition_number(dimension=dimension, cond_num=cond_num)
        
        # Ensure matrix is not None and has the correct shape
        self.assertIsNotNone(matrix_A, "Expected a valid matrix, got None")
        self.assertEqual(matrix_A.shape, (dimension, dimension), "Matrix shape is incorrect")

        # Verify that the matrix has approximately the specified condition number
        computed_cond_num = np.linalg.cond(matrix_A)
        self.assertAlmostEqual(computed_cond_num, cond_num, delta=1e-1, 
                               msg=f"Expected condition number close to {cond_num}, got {computed_cond_num}")

    # Test 4: Check if main function produces y-axis labels in scientific notation
    @patch("matplotlib.pyplot.show")  # Patch plt.show() to prevent the plot from displaying
    def test_main_function_yaxis_labels(self, mock_show):
        """Test that main function generates a plot with y-axis labels in scientific notation (10^x format)."""
        # Purpose: Verify the plot's y-axis labels are in scientific notation.
        # Verifying: Labels like 10^1, 10^2 on the y-axis indicate correct logarithmic scaling.
        # Importance: This ensures the plot is formatted correctly and visually informative.
        
        # Run the main function to generate the plot
        main()
        
        # Access y-axis tick labels
        y_labels = [label.get_text() for label in plt.gca().get_yticklabels()]
        
        # Check that labels contain scientific notation like '10^1', '10^2', etc.
        expected_substrings = ["$10^0$", "$10^1$", "$10^2$", "$10^3$", "$10^4$"]
        label_matches = [any(substring in label for substring in expected_substrings) for label in y_labels]
        
        # Assert that at least one label contains the scientific notation format
        self.assertTrue(any(label_matches), "Expected y-axis labels in scientific notation format (10^x)")
        
        # Close the plot after test to avoid display
        plt.close()

    # Test 5: Verify that the main function creates a plot with at least one line of data
    @patch("matplotlib.pyplot.show")  # Patch plt.show() to prevent the plot from displaying
    def test_main_function_creates_plot_with_line(self, mock_show):
        """Test that main function runs successfully and creates a plot with at least one line."""
        # Purpose: Ensure that calling main() creates a plot with data lines.
        # Verifying: Existence of at least one data line in the plot, confirming plot creation.
        # Importance: Validates that main() successfully produces and populates the plot.
        
        # Run the main function to generate the plot
        main()
        
        # Access the current figure and check if there is at least one line in the plot
        lines = plt.gca().lines
        self.assertGreater(len(lines), 0, "Expected at least one line in the plot")

        # Ensure that the line data is not empty
        y_values = lines[0].get_ydata()
        self.assertGreater(len(y_values), 0, "Expected the line to have y-axis data")

        # Close the plot after test to avoid display
        plt.close()

# Run the tests
if __name__ == '__main__':
    unittest.main(verbosity=2)
