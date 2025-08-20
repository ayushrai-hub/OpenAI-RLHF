import unittest
import numpy as np
from matplotlib.figure import Figure
from testableIC import generate_plot_data, create_energy_charge_plot

class TestEnergyChargePlot(unittest.TestCase):
    #This test ensures that the generated data is of the correct data type (numpy arra)
    def test_generate_plot_data_types(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        self.assertIsInstance(x2, np.ndarray)
        self.assertIsInstance(z1, np.ndarray)
        self.assertIsInstance(z_ticks, np.ndarray)
    # This test checks if the generated data arrays have the correct lengths
    def test_generate_plot_data_lengths(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        self.assertEqual(len(x2), 10)
        self.assertEqual(len(z1), 10)
        self.assertEqual(len(z_ticks), 8)
    # This test checks if the generated data contains the expected values
    def test_generate_plot_data_values(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        np.testing.assert_almost_equal(x2[0], 10)
        np.testing.assert_almost_equal(z1[0], 0.4)
        np.testing.assert_almost_equal(z_ticks[0], 1)
    def test_create_energy_charge_plot_return_type(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        fig = create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks)
        self.assertIsInstance(fig, Figure)
    # This test checks if the plot contains the expecte number of lines
    def test_create_energy_charge_plot_line_count(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        fig = create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks)
        self.assertEqual(len(fig.gca().get_lines()), 7)
    # This test checks if the plot has the correct x and y axis labels
    def test_create_energy_charge_plot_labels(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        fig = create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks)
        self.assertEqual(fig.gca().get_xlabel(), 'Energy (V)')
        self.assertEqual(fig.gca().get_ylabel(), 'Charge (A)')
    # This test checks if the plot has the correct number of y-axis ticks
    def test_create_energy_charge_plot_yticks(self):
        x2, z1, z2, z3, z4, z5, z6, z7, z_ticks = generate_plot_data()
        fig = create_energy_charge_plot(x2, z1, z2, z3, z4, z5, z6, z7, z_ticks)
        self.assertEqual(len(fig.gca().get_yticks()), 8)

if __name__ == '__main__':
    unittest.main(verbosity=2)