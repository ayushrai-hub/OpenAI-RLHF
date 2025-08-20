import unittest
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for headless environments
import matplotlib.pyplot as plt

class TestTickLabelMatching(unittest.TestCase):

    def setUp(self):
        # Common data setup
        self.fig, self.ax = plt.subplots()
        self.z_ticks = [1, 2, 3, 4, 5, 6, 7, 8]
        self.z_labels = [f'{val}.0$\\times$10$^{{-10}}$' for val in self.z_ticks]

    def tearDown(self):
        plt.close(self.fig)

    def test_equal_ticks_and_labels(self):
        """Test that when the number of ticks equals the number of labels, no error is raised."""
        self.ax.set_yticks(self.z_ticks)
        self.ax.set_yticklabels(self.z_labels)
        # If no exception occurs, this test passes.
        self.assertEqual(len(self.ax.get_yticks()), len(self.z_labels), 
                         "The number of ticks should match the number of labels.")

    def test_mismatch_ticks_and_labels_raises_value_error(self):
        """Test that a ValueError is raised when the number of tick labels doesn't match the number of ticks."""
        self.ax.set_yticks(self.z_ticks)
        # Intentionally mismatch by providing fewer labels
        mismatched_labels = self.z_labels[:5]
        with self.assertRaises(ValueError):
            self.ax.set_yticklabels(mismatched_labels)

    def test_dynamic_matching_of_ticks_and_labels(self):
        """Test that we can dynamically adjust the ticks to match a new set of labels without error."""
        # Start with fewer ticks
        initial_ticks = [1, 2, 3, 4]
        initial_labels = [f'{val}.0$\\times$10$^{{-10}}$' for val in initial_ticks]
        self.ax.set_yticks(initial_ticks)
        self.ax.set_yticklabels(initial_labels)

        # Now dynamically update to have more ticks and labels
        new_ticks = self.z_ticks
        new_labels = self.z_labels
        self.ax.set_yticks(new_ticks)
        self.ax.set_yticklabels(new_labels)

        self.assertEqual(len(self.ax.get_yticks()), len(new_labels),
                         "After dynamically adjusting, the number of ticks should match the number of labels.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
