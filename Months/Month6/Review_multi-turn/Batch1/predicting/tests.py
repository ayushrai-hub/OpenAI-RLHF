import unittest
import numpy as np
import pandas as pd
import os
from ideal_completion import (
    simulate_operation,
    drop_below_threshold_probabilities,
    confidence_intervals,
    sensitivity_analysis_on_drones,
    probability_of_retaining_80_percent,
)

class TestIdealCompletion(unittest.TestCase):
    
    def setUp(self):
        self.simulation_runs = 100
        self.operation_length = 14
        self.results_analysis = simulate_operation(
            simulation_runs=self.simulation_runs, operation_length=self.operation_length
        )

        self.critical_thresholds = {
    'Fighter Jets': 35,
    'Drones': 60,
    'Reconnaissance Satellites': 3,
    'Naval Ships': 7
}
        self.initial_assets = {
    'Fighter Jets': 50,
    'Drones': 100,
    'Reconnaissance Satellites': 5,
    'Naval Ships': 10
}
        # Test to check if simulate_operation returns a DataFrame of correct shape and valid thresholds
        # its important to scheck if simulation is running as expected
    def test_simulate_operation(self):
        self.assertIsInstance(self.results_analysis, pd.DataFrame, "Results should be a DataFrame.")
        self.assertEqual(len(self.results_analysis), self.simulation_runs, "Results should match simulation runs.")
        for asset in self.initial_assets.keys():
            self.assertIn(asset, self.results_analysis.columns, f"{asset} should be in results.")

        # Test to check the probability calculation when its dropping below threshold
        #  it important to check probabilty is being  calculated correctly as per user's requirement
    def test_drop_below_threshold_probabilities(self):
        probabilities = drop_below_threshold_probabilities(self.results_analysis, self.critical_thresholds, self.simulation_runs)
        
        for asset, prob in probabilities.items():
            self.assertTrue(0 <= prob <= 100, f"Probability for {asset} should be between 0 and 100.")

        # Test to check if the confidence intervals are within ranges specified.
        # its important as its the  major requirement of user to check the confidence intervals
    def test_confidence_intervals(self):
        intervals = confidence_intervals(self.results_analysis)
        
        for asset, (lower, upper) in intervals.items():
            self.assertLessEqual(lower, upper, f"Lower bound for {asset} should not exceed upper bound.")
            self.assertGreaterEqual(upper, 0, f"Upper bound for {asset} should be non-negative.")

        # Test to check the sensitivity analysis results for drone attrition rates and see if graph is plotted and saved.
        # its important to because graph plotting on sensitivity analysis is requestd by  the  user.
    def test_sensitivity_analysis_on_drones(self):
        sensitivity_mu_values, sensitivity_results = sensitivity_analysis_on_drones(self.simulation_runs, self.operation_length)
        self.assertEqual(len(sensitivity_mu_values), 10, "There should be 10 sensitivity levels.")
        self.assertEqual(len(sensitivity_results), 10, "There should be 10 sensitivity results.")
        image_path = "sensitivity_analysis.png"
        self.assertTrue(os.path.isfile(image_path), "The graph isnot created")
        for i in range(1, len(sensitivity_results)):
            self.assertLessEqual(sensitivity_results[i], sensitivity_results[i-1], 
                                 "Increasing attrition rate should not increase final drone counts.")

        # Test to check the calculation of the probability of retaining at least 80% of assets 
        # its important to check the probabilty of 80 percent  of retaining assets as per the user's requirement.       
    def test_probability_of_retaining_80_percent(self):
        retain_probability = probability_of_retaining_80_percent(self.results_analysis, self.initial_assets, self.simulation_runs)
        
        self.assertTrue(0 <= retain_probability <= 100, "Retention probability should be between 0 and 100.")

if __name__ == "__main__":

    unittest.main(verbosity=2)