import unittest
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from new_ideal_completion import (
    create_voltage_current_plot,
    verify_datasets,
    x2, currents_1, currents_2
)

class TestVoltageCurrent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # It sets up test fixtures before all tests.
        # Prevent plots from being displayed during tests
        plt.switch_backend('Agg')

    def setUp(self):
        # It sets up test fixtures before each test method."""
        self.x_values = x2
        self.test_currents = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        ]
        self.test_y_ticks = [2, 4, 6, 8, 10]
        self.test_y_labels = ['2×10⁻¹⁰', '4×10⁻¹⁰', '6×10⁻¹⁰', '8×10⁻¹⁰', '10×10⁻¹⁰']

    def tearDown(self):
        # It cleans up after each test method.
        plt.close('all')

    def test_create_voltage_current_plot_returns_figure(self):
       # It tests if create_voltage_current_plot returns a matplotlib Figure.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        self.assertIsInstance(fig, Figure)

    def test_plot_axes_labels(self):
        # It testsif plot axes are correctly labeled.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        self.assertEqual(ax.get_xlabel(), 'Energy(V)')
        self.assertEqual(ax.get_ylabel(), 'Charge(A)')

    def test_y_ticks_labels_match(self):
        # It tests if y-ticks and labels are properly set.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        ylabels = [label.get_text() for label in ax.get_yticklabels()]
        self.assertEqual(len(ylabels), len(self.test_y_labels))
        self.assertEqual(ylabels, self.test_y_labels)

    def test_legend_entries(self):
        # It tests if legend entries match temperature labels.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        legend_texts = [text.get_text() for text in ax.get_legend().get_texts()]
        expected_temps = ["(40°C)", "(60°C)", "(120°C)"]
        self.assertEqual(legend_texts[:3], expected_temps)

    def test_data_dimensions(self):
        # It tests if all datasets have correct dimensions.
        # Test Dataset 1
        self.assertEqual(len(currents_1), 7)  # 7 temperature curves
        self.assertTrue(all(len(curve) == 10 for curve in currents_1))  # 10 points each

        # Test Dataset 2
        self.assertEqual(len(currents_2), 7)
        self.assertTrue(all(len(curve) == 10 for curve in currents_2))

    def test_x_axis_range(self):
        # It tests if x-axis range matches input values.
        fig = create_voltage_current_plot(1, self.x_values, self.test_currents, 
                                        self.test_y_ticks, self.test_y_labels)
        ax = fig.gca()
        x_min, x_max = ax.get_xlim()
        # Allow for some padding in the plot
        self.assertLessEqual(x_min, min(self.x_values))
        self.assertGreaterEqual(x_max, max(self.x_values))

    def test_verify_datasets_function(self):
        # It tests if verify_datasets catches mismatched lengths.
        # Redirect stdout to prevent printing during tests
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            verify_datasets()
            sys.stdout = sys.__stdout__
            self.assertIn("All datasets verified successfully!", captured_output.getvalue())
        except AssertionError:
            sys.stdout = sys.__stdout__
            self.fail("verify_datasets() raised AssertionError unexpectedly!")

if __name__ == '__main__':
    unittest.main(verbosity=2)