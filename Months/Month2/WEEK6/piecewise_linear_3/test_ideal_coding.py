import unittest
import numpy as np
import matplotlib.pyplot as plt
from testable_ideal_completion import plot_vsf
class TestPlotFunctions(unittest.TestCase):
    def setUp(self):
        self.separations_VSF = np.logspace(-2, 2, 100)
        self.VSF = np.random.rand(100) * 100
        self.x0, self.x1 = 0, 1
        self.y0 = 1
        self.m1, self.m2, self.m3 = 1, 2, 3
        self.closest_d1, self.closest_f_d1 = 0.5, 50
        self.closest_d2, self.closest_f_d2 = 1.5, 75
        self.x0_2, self.y0_2 = 0.5, 2
        self.m1_2, self.m2_2 = 2, 3
        self.closest_d_2lines, self.closest_f_d_2lines = 0.75, 60
        self.x0_p, self.y0_p = 1, 10
        self.m1_p, self.m2_p = 0.5, 1.5
        self.closest_d, self.closest_f_d = 1.25, 80
        self.without, self.within = 0.1, 10

    def test_piecewise_functions(self):
        x = np.linspace(-1, 2, 100)
        y3 = piecewise_linear_3(x, self.x0, self.x1, self.y0, self.m1, self.m2, self.m3)
        y2 = piecewise_linear(x, self.x0_2, self.y0_2, self.m1_2, self.m2_2)
        yp = piecewise_powerlaw(x, self.x0_p, self.y0_p, self.m1_p, self.m2_p)
        
        self.assertEqual(len(y3), len(x))
        self.assertEqual(len(y2), len(x))
        self.assertEqual(len(yp), len(x))

    def test_create_plots(self):
        fig, axs = create_plots(self.separations_VSF, self.VSF,
                                self.x0, self.x1, self.y0, self.m1, self.m2, self.m3,
                                self.closest_d1, self.closest_f_d1, self.closest_d2, self.closest_f_d2,
                                self.x0_2, self.y0_2, self.m1_2, self.m2_2,
                                self.closest_d_2lines, self.closest_f_d_2lines,
                                self.x0_p, self.y0_p, self.m1_p, self.m2_p,
                                self.closest_d, self.closest_f_d,
                                self.without, self.within)
        
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(axs), 3)

    def test_y_axis_visibility(self):
        fig, axs = create_plots(self.separations_VSF, self.VSF,
                                self.x0, self.x1, self.y0, self.m1, self.m2, self.m3,
                                self.closest_d1, self.closest_f_d1, self.closest_d2, self.closest_f_d2,
                                self.x0_2, self.y0_2, self.m1_2, self.m2_2,
                                self.closest_d_2lines, self.closest_f_d_2lines,
                                self.x0_p, self.y0_p, self.m1_p, self.m2_p,
                                self.closest_d, self.closest_f_d,
                                self.without, self.within)
        
        self.assertTrue(axs[0].yaxis.get_visible())
        self.assertFalse(axs[1].yaxis.get_visible())
        self.assertFalse(axs[2].yaxis.get_visible())

if __name__ == '__main__':
    unittest.main(verbosity=2)


    fjhfjhggxhzxhrdfbxfbxzxbfzfzfhxhdgbcxbv nbghmc vcngcmhcgncngcgnxxgn n