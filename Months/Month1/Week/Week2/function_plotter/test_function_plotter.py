import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from vispy.color import Colormap

# Mock QApplication for testing
app = QApplication([])

# Import your FunctionPlotter class
from function_plotter import FunctionPlotter

class TestFunctionPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = FunctionPlotter()

    def test_initial_parameters(self):
        self.assertEqual(self.plotter.a, 1)
        self.assertEqual(self.plotter.b, 1)
        self.assertEqual(self.plotter.c, 0)
        self.assertEqual(self.plotter.function_input, "np.sin(X) + np.cos(Y)")
        self.assertEqual(self.plotter.GRID_POINTS, 50)
        self.assertEqual(self.plotter.X_LIMITS, (-5, 5))
        self.assertEqual(self.plotter.Y_LIMITS, (-5, 5))

    def test_create_function(self):
        X, Y, Z = self.plotter.create_function(1, 1, 0)
        self.assertEqual(X.shape, (50, 50))
        self.assertEqual(Y.shape, (50, 50))
        self.assertEqual(Z.shape, (50, 50))

    def test_colormap_initialization(self):
        colormap_name = self.plotter.props.combo.currentText()
        self.assertIsInstance(self.plotter.cm, Colormap)

    @patch('vispy.scene.visuals.SurfacePlot')
    def test_plot_function(self, mock_surface_plot):
        mock_surface = MagicMock()
        mock_surface_plot.return_value = mock_surface

        self.plotter.surface = mock_surface
        self.plotter.plot_function(self.plotter.X, self.plotter.Y, self.plotter.Z)
        
        mock_surface.set_data.assert_called_once()
        mock_surface.mesh_data.set_vertex_colors.assert_called_once()

    def test_update_grid_points(self):
        self.plotter.props.grid_points.setValue(100)
        QTest.qWait(100)  # Wait for changes to take effect
        self.plotter.update_grid_points()
        self.assertEqual(self.plotter.GRID_POINTS, 100)
        self.assertEqual(self.plotter.X.shape, (100, 100))
        self.assertEqual(self.plotter.Y.shape, (100, 100))
        self.assertEqual(self.plotter.Z.shape, (100, 100))

    def test_update_function(self):
        self.plotter.props.function_input.setText("np.sin(X) * np.cos(Y)")
        self.plotter.update_function()
        self.assertEqual(self.plotter.function_input, "np.sin(X) * np.cos(Y)")
        self.assertEqual(self.plotter.X.shape, (self.plotter.GRID_POINTS, self.plotter.GRID_POINTS))
        self.assertEqual(self.plotter.Y.shape, (self.plotter.GRID_POINTS, self.plotter.GRID_POINTS))
        self.assertEqual(self.plotter.Z.shape, (self.plotter.GRID_POINTS, self.plotter.GRID_POINTS))

    def test_get_scaled_value(self):
        self.plotter.time = np.pi / 2
        self.assertAlmostEqual(self.plotter.get_scaled_value(0, 1), 1)  # sin(pi/2) = 1
        self.assertAlmostEqual(self.plotter.get_scaled_value(1, 1), 0, places=7)  # cos(pi/2) = 0
        self.assertAlmostEqual(self.plotter.get_scaled_value(2, 1), 16331239353195370)  # tan(pi/2) is undefined, but np.tan returns a large value
        self.assertEqual(self.plotter.get_scaled_value(3, 1), 1)  # static value

    def test_update_x_limits(self):
        initial_x_limits = self.plotter.X_LIMITS
        self.plotter.props.x_limits.setValue(7)
        self.plotter.update_x_limits()
        self.assertEqual(self.plotter.X_LIMITS, (-7, 7))
        self.assertNotEqual(self.plotter.X_LIMITS, initial_x_limits)

    def test_update_y_limits(self):
        initial_y_limits = self.plotter.Y_LIMITS
        self.plotter.props.y_limits.setValue(8)
        self.plotter.update_y_limits()
        self.assertEqual(self.plotter.Y_LIMITS, (-8, 8))
        self.assertNotEqual(self.plotter.Y_LIMITS, initial_y_limits)

    def test_update_colormap(self):
        initial_colormap = self.plotter.cm
        self.plotter.props.combo.setCurrentText('plasma')
        self.plotter.update_colormap()
        self.assertNotEqual(self.plotter.cm, initial_colormap)

    def tearDown(self):
        self.plotter.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)