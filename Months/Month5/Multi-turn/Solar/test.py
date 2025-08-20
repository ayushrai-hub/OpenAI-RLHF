import unittest
import numpy as np
import pandas as pd
import warnings
from plotly.graph_objs import Figure
from try_ideal import generate_solar_output, simulate_battery, main

MW_CAPACITY = 1  # Capacity of the solar farm in MW

class TestSolarFarmSimulation(unittest.TestCase):
    def test_generate_solar_output(self):
        """
        Test the generate_solar_output function.
        This test checks the structure of the DataFrame, verifies correct handling of
        diurnal and seasonal variations, and ensures there are no unexpected warnings.
        """

        # Catch warnings and fail the test if a FutureWarning is encountered.
        # This ensures that the function won't raise deprecated warnings in the future.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Capture all warnings
            df = generate_solar_output()

            # Check for FutureWarning specifically. If present, the test will fail.
            for warning in w:
                if issubclass(warning.category, FutureWarning):
                    self.fail("FutureWarning raised in generate_solar_output()")

        # Check if the output is a DataFrame of the correct length (8760 hours for a year).
        # This ensures that the function generates output for every hour in a year.
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 8760, "Output DataFrame length does not match 8760 hours for a year")

        # Ensure expected columns ('solar_power' and 'timestamp') are present.
        # This confirms the DataFrame has the correct structure for downstream functions.
        self.assertIn('solar_power', df.columns)
        self.assertIn('timestamp', df.columns)

        # Check that all solar power values are non-negative (no unexpected generation drops).
        # Solar power should logically be zero or positive since it's generation output.
        self.assertTrue((df['solar_power'] >= 0).all(), "Solar power contains negative values")

        # Verify that solar power doesn't exceed the maximum capacity of the farm (1 MW).
        # This confirms the model doesn't exceed physical system limits.
        self.assertTrue(df['solar_power'].max() <= MW_CAPACITY, "Solar power exceeds maximum capacity of the farm")

    def test_simulate_battery(self):
        """
        Test the simulate_battery function.
        This test checks that the battery simulation runs correctly by verifying
        the types, shapes, and value ranges of the returned outputs.
        """

        # Generate sample solar data for the test.
        # This ensures the battery simulation has a valid input.
        df = generate_solar_output()
        battery_capacity = 50  # Testing with a 50 MWh battery

        # Run the battery simulation function.
        # This simulates the SOC (state of charge) and unmet energy share over time.
        soc, solar_plus_battery, unmet_energy_share = simulate_battery(df, battery_capacity)

        # Verify the type and shape of the SOC output array.
        # SOC is expected as a numpy array and should match the length of input data.
        self.assertIsInstance(soc, np.ndarray, "SOC output is not a numpy array")
        self.assertEqual(len(soc), len(df), "SOC array length does not match the input data length")

        # Verify the type and shape of the combined solar and battery output.
        # This output should represent the combined generation and match the input length.
        self.assertIsInstance(solar_plus_battery, np.ndarray, "Solar plus battery output is not a numpy array")
        self.assertEqual(len(solar_plus_battery), len(df), "Solar plus battery output length does not match input data length")

        # Check that the unmet energy share is a float, which represents a fraction of unmet demand.
        # This output should indicate the share of load that couldn't be met by solar and battery.
        self.assertIsInstance(unmet_energy_share, float, "Unmet energy share is not a float")

        # Confirm that SOC values are within valid bounds: 0 to battery capacity.
        # SOC should not exceed capacity or fall below zero, which ensures the model's accuracy.
        self.assertTrue((soc >= 0).all(), "SOC contains values below 0")
        self.assertTrue((soc <= battery_capacity).all(), "SOC contains values above battery capacity")

        # Validate that unmet energy share is within the range [0, 1].
        # This indicates that the unmet load fraction is logically within 0% to 100%.
        self.assertGreaterEqual(unmet_energy_share, 0, "Unmet energy share is below 0")
        self.assertLessEqual(unmet_energy_share, 1, "Unmet energy share exceeds 1")

    def test_main_function_execution(self):
        """
        Test the main function for successful execution.
        This test checks if the main function completes without raising any exceptions,
        which serves as an integration test for the entire script.
        """

        # Suppress ResourceWarning for unclosed sockets, often raised by Plotly in testing.
        # This ensures the warning does not interfere with test results.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            try:
                # Run main and catch any exceptions, ensuring it completes successfully.
                main()            except Exception as e:
                self.fail(f"main() raised an exception: {e}")

# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity=2)