import unittest
import numpy as np
from original_code import create_surface_plot

class TestSurfacePlot(unittest.TestCase):
    def test_create_surface_plot_returns_figure(self):
        fig = create_surface_plot()
        self.assertIsNotNone(fig)
        self.assertEqual(type(fig).__name__, 'Figure')

    def test_create_surface_plot_custom_ranges(self):
        fig = create_surface_plot(x_range=(-10, 10), y_range=(-8, 8), num_points=100)
        self.assertIsNotNone(fig)
        self.assertEqual(type(fig).__name__, 'Figure')
        
        # Check if the data has the correct shape
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(len(fig.data[0].x), 100)
        self.assertEqual(len(fig.data[0].y), 100)
        self.assertEqual(fig.data[0].z.shape, (100, 100))

    def test_create_surface_plot_layout(self):
        fig = create_surface_plot()
        
        # Check if the layout is correctly set
        self.assertEqual(fig.layout.title.text, '3D Surface Plot with Plotly')
        self.assertEqual(fig.layout.scene.xaxis.title.text, 'X Axis')
        self.assertEqual(fig.layout.scene.yaxis.title.text, 'Y Axis')
        self.assertEqual(fig.layout.scene.zaxis.title.text, 'Z Axis')

if __name__ == '__main__':
    unittest.main(verbosity=2)