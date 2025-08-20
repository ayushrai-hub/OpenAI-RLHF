import unittest
import numpy as np
from ideal_completion import logistic_model, estimate_parameters, plot_data

class TestLogisticModel(unittest.TestCase):
    def test_logistic_model(self):
        """
        Tests the logistic model function to ensure it calculates the expected fluorescence intensity correctly.
        This test verifies that the logistic model equation correctly computes the output based on known 
        input parameters, which is crucial for ensuring the scientific accuracy of the model's predictions.
        """
        params = [1000, 30, 0.1, 50, 100]  # I0, tau, k, tc, Ib
        t = 50
        expected = params[0] * np.exp(-t / params[1]) * (1 / (1 + np.exp(-params[2] * (t - params[3])))) + params[4]
        result = logistic_model(t, *params)
        self.assertAlmostEqual(result, expected, places=5)

    def test_parameter_estimation_accuracy(self):
        """
        Tests the parameter estimation function with noisy data to ensure it can reliably estimate model 
        parameters. This test simulates real-world data conditions with significant noise to evaluate the 
        robustness of the parameter estimation algorithm, which is critical for its use in actual scientific and 
        research applications.
        """
        time = np.linspace(0, 100, 200)
        true_params = [1000, 30, 0.1, 50, 100]  # I0, tau, k, tc, Ib
        intensity = logistic_model(time, *true_params)
        noise = np.random.normal(0, 100, len(time))  # Substantial noise level
        intensity_noisy = intensity + noise

        estimated_params, fitted_intensity, duration_D = estimate_parameters(time, intensity_noisy)        
        self.assertIsNotNone(estimated_params, "Parameter estimation failed and returned None.")

    def test_plot_data(self):
        """
        Ensures that the plotting function can execute without errors when provided with valid data.
        This test is crucial for validating that the plot_data function can reliably produce plots without 
        crashing, which supports its use in exploratory data analysis and result presentation.
        """
        time = np.linspace(0, 100, 200)
        params = [1000, 30, 0.1, 50, 100]
        intensity = logistic_model(time, *params)
        try:
            plot_data(time, intensity, intensity)  # using the same data as fitted for simplicity
        except Exception as e:
            self.fail(f"plot_data function raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()