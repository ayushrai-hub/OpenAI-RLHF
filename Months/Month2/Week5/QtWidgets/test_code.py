import unittest
import numpy as np
from PyQt5.QtWidgets import QApplication
from original_code import FunctionPlotter

class TestFunctionPlotter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.plotter = FunctionPlotter()

    def test_initialization(self):
        self.assertEqual(self.plotter.time, 0)
        self.assertEqual(self.plotter.a, 1)
        self.assertEqual(self.plotter.b, 1)
        self.assertEqual(self.plotter.c, 0)
        self.assertIsInstance(self.plotter.X, np.ndarray)
        self.assertIsInstance(self.plotter.Y, np.ndarray)
        self.assertIsInstance(self.plotter.Z, np.ndarray)

    def test_create_function(self):
        self.plotter._function_input = "a * X**2 + b * Y**2 + c"
        X, Y, Z = self.plotter._create_function(1, 2, 3)
        self.assertEqual(X.shape, Y.shape)
        self.assertEqual(Y.shape, Z.shape)
        np.testing.assert_allclose(Z, X**2 + 2*Y**2 + 3)

    def test_update_limits(self):
        initial_x = self.plotter._x_limits
        initial_y = self.plotter._y_limits
        self.plotter.props.x_limits.setValue(7)
        self.plotter.update_x_limits()
        self.assertEqual(self.plotter._x_limits, (-7, 7))
        self.plotter.props.y_limits.setValue(8)
        self.plotter.update_y_limits()
        self.assertEqual(self.plotter._y_limits, (-8, 8))
        self.assertNotEqual(self.plotter._x_limits, initial_x)
        self.assertNotEqual(self.plotter._y_limits, initial_y)

    def test_update_grid_points(self):
        initial_grid = self.plotter._grid_points
        self.plotter.props.grid_points.setValue(75)
        self.plotter.update_grid_points()
        self.assertEqual(self.plotter._grid_points, 75)
        self.assertNotEqual(self.plotter._grid_points, initial_grid)

    def test_update_function(self):
        initial_func = self.plotter._function_input
        self.plotter.props.function_input.setText("np.sin(X) + np.cos(Y)")
        self.plotter.update_function()
        self.assertEqual(self.plotter._function_input, "np.sin(X) + np.cos(Y)")
        self.assertNotEqual(self.plotter._function_input, initial_func)

    def test_get_scaled_value(self):
        self.assertEqual(FunctionPlotter._get_scaled_value(3, 1.0), 1)  # static
        self.assertAlmostEqual(FunctionPlotter._get_scaled_value(0, 1.0), np.sin(0.1), places=5)  # sin
        self.assertAlmostEqual(FunctionPlotter._get_scaled_value(1, 1.0), np.cos(0.1), places=5)  # cos
        self.assertAlmostEqual(FunctionPlotter._get_scaled_value(2, 1.0), np.tan(0.1), places=5)  # tan

    def test_invalid_function(self):
        self.plotter._function_input = "invalid_function(X, Y)"
        X, Y, Z = self.plotter._create_function(1, 1, 1)
        np.testing.assert_array_equal(Z, np.zeros_like(X))  # Should return zero array for invalid function

if __name__ == '__main__':
    unittest.main(verbosity=2)