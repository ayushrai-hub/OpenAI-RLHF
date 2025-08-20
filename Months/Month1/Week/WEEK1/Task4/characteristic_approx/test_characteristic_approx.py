import unittest
import numpy as np

from ideal_completion import characteristic_approx
def characteristic_approx(x, a, b):
    return 0.5 * (np.tanh((x + a) / b) - np.tanh((x - a) / b))

class TestCharacteristicApprox(unittest.TestCase):
    def setUp(self):
        self.a = 2
        self.b_values = [0.1, 0.5, 1.0]
        self.x = np.linspace(-4, 4, 1000)

    def test_range(self):
        for b in self.b_values:
            y = characteristic_approx(self.x, self.a, b)
            self.assertTrue(np.all(y >= 0) and np.all(y <= 1),
                            f"Output should be in [0, 1] range for b={b}")

    def test_symmetry(self):
        for b in self.b_values:
            y = characteristic_approx(self.x, self.a, b)
            self.assertTrue(np.allclose(y, np.flip(y)),
                            f"Function should be symmetric for b={b}")

    def test_interval_boundaries(self):
        for b in self.b_values:
            left_boundary = characteristic_approx(-self.a, self.a, b)
            right_boundary = characteristic_approx(self.a, self.a, b)
            self.assertAlmostEqual(left_boundary, 0.5, delta=1e-3,
                                   msg=f"Left boundary should be close to 0.5 for b={b}")
            self.assertAlmostEqual(right_boundary, 0.5, delta=1e-3,
                                   msg=f"Right boundary should be close to 0.5 for b={b}")

    def test_integral(self):
        for b in self.b_values:
            y = characteristic_approx(self.x, self.a, b)
            integral = np.trapezoid(y, self.x)
            self.assertAlmostEqual(integral, 2*self.a, delta=0.1,
                                   msg=f"Integral should be close to {2*self.a} for b={b}")

    def test_steepness(self):
        x_test = np.linspace(-self.a, self.a, 100)
        y_values = [characteristic_approx(x_test, self.a, b) for b in self.b_values]
        for i in range(len(self.b_values) - 1):
            self.assertTrue(np.all(y_values[i] >= y_values[i+1]),
                            f"Curve for b={self.b_values[i]} should be steeper than b={self.b_values[i+1]}")

if __name__ == '__main__':
    unittest.main(verbosity=2)