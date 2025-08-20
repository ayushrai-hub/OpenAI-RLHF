import unittest
from unittest.mock import patch, call, Mock
import io
import sys
from testable_ideal_solution import main

class TestMainFunction(unittest.TestCase):

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_output(self, mock_stdout):
        main()
        output = mock_stdout.getvalue().strip().split('\n')
        
        self.assertIn("The mesh is closed.", output[0])
        self.assertIn("No boundary edges in a closed mesh.", output[1])
        
        sharp_edges_line = next((line for line in output if "Number of sharp edges:" in line), None)
        self.assertIsNotNone(sharp_edges_line)
        num_sharp_edges = int(sharp_edges_line.split(":")[1].strip())
        self.assertEqual(num_sharp_edges, 12)
        
        sharp_vertices_line = next((line for line in output if "Number of sharp vertices:" in line), None)
        self.assertIsNotNone(sharp_vertices_line)
        num_sharp_vertices = int(sharp_vertices_line.split(":")[1].strip())
        self.assertEqual(num_sharp_vertices, 8)

    @patch('matplotlib.pyplot.show')
    def test_visualization_called(self, mock_show):
        main()
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.title')
    def test_plot_creation(self, mock_title, mock_figure):
        # Create a mock for the Figure object
        mock_fig = Mock()
        mock_figure.return_value = mock_fig
        
        # Create a mock for the Axes object
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax
        
        main()
        
        # Check if figure() was called
        mock_figure.assert_called()
        
        # Check if add_subplot was called with the correct arguments
        mock_fig.add_subplot.assert_called_with(111, projection='3d')
        
        # Check if the correct plotting methods were called
        self.assertEqual(mock_ax.scatter.call_count, 2)  # All vertices and sharp vertices
        self.assertGreater(mock_ax.plot.call_count, 0)  # Edges
        mock_ax.set_xlabel.assert_called_with('X')
        mock_ax.set_ylabel.assert_called_with('Y')
        mock_ax.set_zlabel.assert_called_with('Z')
        mock_ax.legend.assert_called_once()
        
        # Check if the title was set using plt.title()
        mock_title.assert_called_with('3D Mesh with Sharp Vertices Highlighted')

if __name__ == '__main__':
    unittest.main(verbosity=2)