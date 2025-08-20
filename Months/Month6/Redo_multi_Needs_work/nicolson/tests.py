import unittest
import numpy as np
from ideal_completion import crank_nicolson_2D_sphere


class TestPythonCode(unittest.TestCase):

    def test_value_error_occurrence(self):
        # This test is meant to verify if the ValueError is still raised
        t_limit = 10.0  # seconds
        radius = 1.0  # meters
        theta = np.pi  # radians
        d_radius = 0.05  # meters
        d_theta = np.pi / 16  # radians
        d_time = 0.1  # seconds
        beta = 1e-5  # m^2/s
        Initial_Temp = 20.0  # degrees
        Energy = 500.0  # Joules
        impulse_time = 1.0  # seconds
        conv = 5.0  # convection coefficient
        specific_heat = 900.0  # J/kg°C
        density = 7800.0  # kg/m³
        try:
            crank_nicolson_2D_sphere(
                t_limit, radius, theta, d_radius, d_theta, d_time, beta,
                Initial_Temp, Energy, impulse_time, conv, specific_heat,
                density)
        except ValueError:
            self.fail("Value Error has been raised")

    def test_temperature_function_consistency(self):
        # This test is meant to verify if the rest of the solution generate
        # a consistent array of temperatures
        t_limit = 10.0  # seconds
        radius = 1.0  # meters
        theta = np.pi  # radians
        d_radius = 0.05  # meters
        d_theta = np.pi / 16  # radians
        d_time = 0.1  # seconds
        beta = 1e-5  # m^2/s
        Initial_Temp = 20.0  # degrees
        Energy = 500.0  # Joules
        impulse_time = 1.0  # seconds
        conv = 5.0  # convection coefficient
        specific_heat = 900.0  # J/kg°C
        density = 7800.0  # kg/m³
        temps, times = crank_nicolson_2D_sphere(
            t_limit, radius, theta, d_radius, d_theta, d_time, beta,
            Initial_Temp, Energy, impulse_time, conv, specific_heat,
            density)
        expected_result = 97.06171376882246
        if abs(sum(temps) - expected_result) > 0.05:
            self.assertTrue(f'Expected sum of temps {expected_result}. Found sum of temps: {sum(temps)}')

    def test_time_function_consistency(self):
        # This test is meant to verify if the rest of the solution generate
        # a consistent array of times
        t_limit = 10.0  # seconds
        radius = 1.0  # meters
        theta = np.pi  # radians
        d_radius = 0.05  # meters
        d_theta = np.pi / 16  # radians
        d_time = 0.1  # seconds
        beta = 1e-5  # m^2/s
        Initial_Temp = 20.0  # degrees
        Energy = 500.0  # Joules
        impulse_time = 1.0  # seconds
        conv = 5.0  # convection coefficient
        specific_heat = 900.0  # J/kg°C
        density = 7800.0  # kg/m³
        temps, times = crank_nicolson_2D_sphere(
            t_limit, radius, theta, d_radius, d_theta, d_time, beta,
            Initial_Temp, Energy, impulse_time, conv, specific_heat,
            density)

        expected_result = [
            0.0, 0.10101010101010101, 0.20202020202020202, 0.30303030303030304,
            0.40404040404040403, 0.5050505050505051, 0.6060606060606061, 0.7070707070707071,
            0.8080808080808081, 0.9090909090909091, 1.0101010101010102, 1.1111111111111112,
            1.2121212121212122, 1.3131313131313131, 1.4141414141414141, 1.5151515151515151,
            1.6161616161616161, 1.7171717171717171, 1.8181818181818181, 1.9191919191919191,
            2.0202020202020203, 2.121212121212121, 2.2222222222222223, 2.323232323232323,
            2.4242424242424243, 2.525252525252525, 2.6262626262626263, 2.727272727272727,
            2.8282828282828283, 2.929292929292929, 3.0303030303030303, 3.131313131313131,
            3.2323232323232323, 3.3333333333333335, 3.4343434343434343, 3.5353535353535355,
            3.6363636363636362, 3.7373737373737375, 3.8383838383838382, 3.9393939393939394,
            4.040404040404041, 4.141414141414141, 4.242424242424242, 4.343434343434343,
            4.444444444444445, 4.545454545454545, 4.646464646464646, 4.747474747474747,
            4.848484848484849, 4.94949494949495, 5.05050505050505, 5.151515151515151,
            5.252525252525253, 5.353535353535354, 5.454545454545454, 5.555555555555555,
            5.656565656565657, 5.757575757575758, 5.858585858585858, 5.959595959595959,
            6.0606060606060606, 6.161616161616162, 6.262626262626262, 6.363636363636363,
            6.4646464646464645, 6.565656565656566, 6.666666666666667, 6.767676767676767,
            6.8686868686868685, 6.96969696969697, 7.070707070707071, 7.171717171717171,
            7.2727272727272725, 7.373737373737374, 7.474747474747475, 7.575757575757575,
            7.6767676767676765, 7.777777777777778, 7.878787878787879, 7.979797979797979,
            8.080808080808081, 8.181818181818182, 8.282828282828282, 8.383838383838384,
            8.484848484848484, 8.585858585858587, 8.686868686868687, 8.787878787878787,
            8.88888888888889, 8.98989898989899, 9.09090909090909, 9.191919191919192,
            9.292929292929292, 9.393939393939394, 9.494949494949495, 9.595959595959595,
            9.696969696969697, 9.797979797979798, 9.8989898989899, 10.0]
        result = [float(elem) == expected_result[i] for i, elem in enumerate(list(times))]
        self.assertTrue(all(result))


if __name__ == "__main__":
    unittest.main(verbosity=2)
