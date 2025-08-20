import unittest
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from ideal_completion import (

    create_voltage_current_plot,
    verify_datasets,
    x2, currents_1, currents_2, currents_3, currents_4,
    y_ticks_1, y_labels_1, y_ticks_2, y_labels_2,
    y_ticks_3, y_labels_3, y_ticks_4, y_labels_4
)

class TestVoltageCurrent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        plt.switch_backend('Agg')

    def setUp(self):
        # Create proper test data with 7 temperature curves, 10 points each.
        # This standardized test data ensure concistent testing conditionsacross all test method.
        self.x_values = x2
        self.test_currents = [
            [i + j for j in range(10)] for i in range(7)
        ]
        self.test_y_ticks = [2, 4, 6, 8, 10]
        self.test_y_labels = ['2×10⁻¹⁰', '4×10⁻¹⁰', '6×10⁻¹⁰', '8×10⁻¹⁰', '10×10⁻¹⁰']
        self.expected_markers = ['s', 'o', '<', '>', 'v', '^', 'D']

    def tearDown(self):
        plt.close('all')

    def test_create_voltage_current_plot_returns_figure(self):
        # It tests if create_voltage_current_plot returns a matplotlib Figure.
        # This is crucial because the test code expects a Figure object for proper rendering and manipulation. If this tests fails it indicates a issue in the plot creation.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        self.assertIsInstance(fig, Figure)

    def test_plot_axes_labels(self):
        # It tests if plot axes are correctly labeled.
        # Proper labelling is essential for data interpretation and scientific accuracy.
        # Mislabelled axes could lead to incorrect data interpretation and potentially invalid scientific conclusions.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        self.assertEqual(ax.get_xlabel(), 'Energy(V)')
        self.assertEqual(ax.get_ylabel(), 'Charge(A)')

    def test_markers_used_correctly(self):
        # It checks if the required markers (['s', 'o', '<', '>', 'v', '^', 'D']) are being used.
        # Different markers are crucial for distinguishing between temperature curves. 
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        lines = [line for line in ax.get_lines() if isinstance(line, Line2D)]
        markers_used = [line.get_marker() for line in lines]
        self.assertEqual(markers_used, self.expected_markers)

    def test_all_datasets_structure(self):
        # It tests the structure of all datasets.
        # structure is critical because: The seven curves represent specific temperatures that must all be present.
        # Each curve needs exactly 10 points for proper voltage-current relationship analysis.
        # Inconsistent data structure could cause plotting failures or misleading visualizations.
        datasets = [currents_1, currents_2, currents_3, currents_4]
        for i, currents in enumerate(datasets, 1):
            with self.subTest(dataset=i):
                self.assertEqual(len(currents), 7, f"Dataset {i} must have 7 curves")
                for j, curve in enumerate(currents):
                    self.assertEqual(len(curve), 10, 
                                  f"Dataset {i}, curve {j} must have 10 points")

    def test_verify_datasets_catches_errors(self):
        # It tests if verify_datasets catches mismatched lengths.
        # Test with invalid dataset. This validation is important because invalid datasets could crash the plotting function.
        invalid_currents = [[1, 2, 3,4, 5, 6, 7, 8, 9, 10]] * 6 
        invalid_dataset = [(invalid_currents, self.test_y_ticks, self.test_y_labels)]
        
        result = verify_datasets(invalid_dataset)
        self.assertFalse(result, "verify_datasets should return False for invalid")

    def test_verify_all_real_datasets(self):
        # This confirms that all actual experimental datasets pass validation
        # This test is crucial because, it ensures that our real experimental data meets all requirements
        datasets = [
            (currents_1, y_ticks_1, y_labels_1),
            (currents_2, y_ticks_2, y_labels_2),
            (currents_3, y_ticks_3, y_labels_3),
            (currents_4, y_ticks_4, y_labels_4)
        ]
        try:
            result = verify_datasets(datasets)
            self.assertTrue(result)
        except ValueError as e:
            self.fail(f"verify_datasets() raised ValueError unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)