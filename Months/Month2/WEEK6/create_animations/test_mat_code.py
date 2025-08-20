import unittest
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def create_animations(num_animations=3, interval=50, frames=200):
    fig, axs = plt.subplots(1, num_animations, figsize=(5 * num_animations, 5))
    
    if num_animations == 1:
        axs = [axs]
    
    lines = []
    animations = []

    for i in range(num_animations):
        x = np.linspace(0, 2 * np.pi, 128)
        y = np.sin(x) * np.cos((i + 1) * x)
        line, = axs[i].plot(x, y, color=np.random.rand(3,))
        lines.append(line)

        def update(frame, line=line, x=x, i=i):
            y = np.sin(x + frame / 10.0 + i) * np.cos(x + frame / 15.0 + i)
            line.set_ydata(y)
            return line,

        ani = FuncAnimation(fig, update, frames=frames, blit=True, interval=interval)
        animations.append(ani)

    return fig, axs, animations

class TestAnimationFunction(unittest.TestCase):

    def setUp(self):
        plt.close('all')  # Close any open plots before each test

    def test_basic_functionality(self):
        fig, axs, animations = create_animations(3)
        self.assertEqual(len(axs), 3)
        self.assertEqual(len(animations), 3)
        plt.close(fig)

    def test_single_animation(self):
        fig, axs, animations = create_animations(1)
        self.assertIsInstance(axs, list)
        self.assertEqual(len(axs), 1)
        self.assertEqual(len(animations), 1)
        plt.close(fig)

    def test_large_number_of_animations(self):
        fig, axs, animations = create_animations(10)
        self.assertEqual(len(axs), 10)
        self.assertEqual(len(animations), 10)
        plt.close(fig)

    def test_zero_animations(self):
        with self.assertRaises(ValueError):
            create_animations(0)

    def test_negative_animations(self):
        with self.assertRaises(ValueError):
            create_animations(-1)

    def test_animation_properties(self):
        fig, axs, animations = create_animations(3, interval=100, frames=150)
        self.assertEqual(animations[0]._save_count, 150)
        self.assertEqual(animations[0]._interval, 100)
        plt.close(fig)

    def test_subplot_types(self):
        fig, axs, animations = create_animations(3)
        for ax in axs:
            self.assertIsInstance(ax, plt.Axes)
        plt.close(fig)

    def test_line_objects(self):
        fig, axs, animations = create_animations(3)
        for ax in axs:
            self.assertEqual(len(ax.lines), 1)
            self.assertIsInstance(ax.lines[0], plt.Line2D)
        plt.close(fig)

if __name__ == '__main__':
    unittest.main(verbosity=2)