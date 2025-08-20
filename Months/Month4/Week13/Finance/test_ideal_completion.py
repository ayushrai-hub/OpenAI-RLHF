import unittest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from ideal_completion1 import BondAnalyzer

class TestBondAnalyzer(unittest.TestCase):
    def setUp(self):
        # It initializes test data with realistic market rates and bond prices
        self.libor_3m = 0.01472717
        self.libor_6m = 0.01893706
        self.base_prices = [
            102.33689177,
            104.80430234,
            105.1615306,
            105.6581905,
            104.028999992,
            101.82604116
        ]
        self.analyzer = BondAnalyzer(self.libor_3m, self.libor_6m, self.base_prices)

    def test_initialization(self):
        # This tests proper initilization of BondAnalyzer class, 
        self.assertEqual(self.analyzer.libor_3m, self.libor_3m)
        self.assertEqual(self.analyzer.libor_6m, self.libor_6m)
        assert_array_almost_equal(self.analyzer.bond_prices, np.array(self.base_prices))
        self.assertEqual(len(self.analyzer.bonds), 6)
        self.assertEqual(self.analyzer.scenario, 'base')

    def test_january_scenario_initialization(self):
        # It tests the initialization with January scenario.
        january_prices = self.base_prices + [99.05, 97.82, 96.43, 95.01]
        jan_analyzer = BondAnalyzer(self.libor_3m, self.libor_6m, january_prices, 'january')
        self.assertEqual(len(jan_analyzer.bonds), 10)
        self.assertEqual(jan_analyzer.scenario, 'january')

    def test_generate_payment_times(self):
        # It tests the payment times generation.
        payment_times = self.analyzer.generate_payment_times()
        self.assertTrue(all(t > 0 for t in payment_times))
        self.assertTrue(all(payment_times[i] < payment_times[i+1] 
                          for i in range(len(payment_times)-1)))
        self.assertLessEqual(max(payment_times), 2.0)

    def test_cashflow_matrix_shape(self):
        # It tests the dimensions of cashflow matrix.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        n_bonds = len(self.analyzer.bonds)
        n_times = len(self.analyzer.payment_times)
        self.assertEqual(cf_matrix.shape, (n_bonds, n_times))

    def test_cashflow_matrix_values(self):
        # It tests the specific values in cashflow matrix.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        
        # It tests  first bond (quarterly, 4% coupon)
        first_bond_flows = cf_matrix[0]
        quarterly_coupon = 4.0 / 4  # 4% annual paid quarterly
        self.assertAlmostEqual(first_bond_flows[3], quarterly_coupon + 100)  # Final payment
        
        # It tests  second bond (semi-annual, 5% coupon)
        second_bond_flows = cf_matrix[1]
        semi_annual_coupon = 5.0 / 2  # 5% annual paid semi-annually
        self.assertAlmostEqual(second_bond_flows[1], semi_annual_coupon)

    def test_forward_rates_calculation(self):
        # It tests the forward rates calculation.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        zero_rates = self.analyzer.calibrate_zero_rates(cf_matrix)
        forward_rates = self.analyzer.calculate_forward_rates(zero_rates)
        
        self.assertEqual(len(forward_rates), len(self.analyzer.payment_times) - 1)
        self.assertTrue(all(rate > 0 for rate in forward_rates))
        self.assertTrue(all(rate < 0.15 for rate in forward_rates))

    def test_swap_rate_calculation(self):
        # It tests the swap rate calculation.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        zero_rates = self.analyzer.calibrate_zero_rates(cf_matrix)
        swap_rate = self.analyzer.calculate_swap_rate(zero_rates)
        
        self.assertTrue(0 < swap_rate < 0.15)  # Reasonable bounds for swap rate

    def test_receiver_swap_pricing(self):
        # It tests the receiver swap pricing.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        zero_rates = self.analyzer.calibrate_zero_rates(cf_matrix)
        swap_price = self.analyzer.price_receiver_swap(zero_rates, notional=1000000)
        
        # Test if swap price is within reasonable bounds
        self.assertTrue(abs(swap_price) < 100000)  # Should be less than 10% of notional

    def test_arbitrage_detection(self):
        # It tests the  arbitrage opportunities detection.
        cf_matrix = self.analyzer.build_cashflow_matrix()
        zero_rates = self.analyzer.calibrate_zero_rates(cf_matrix)
        opportunities = self.analyzer.check_arbitrage(zero_rates)
        
        # Verify structure of arbitrage opportunities
        for opp in opportunities:
            self.assertTrue('bond_index' in opp)
            self.assertTrue('action' in opp)
            self.assertTrue('price_difference' in opp)
            self.assertTrue('market_price' in opp)
            self.assertTrue('model_price' in opp)
            self.assertTrue(opp['price_difference'] > 0.0005)  # Above transaction cost

    def test_ols_parameter_estimation(self):
        # It tests the  OLS parameter estimation.
        params = self.analyzer.estimate_parameters_ols()
        
        self.assertEqual(len(params), 3)  # Should have three parameters
        self.assertTrue(all(isinstance(p, float) for p in params))

    def test_final_scenario_analysis(self):
        # It tests the  final scenario analysis.
        final_prices = [
            102.45,
            104.92,
            105.28,
            105.78,
            104.15,
            101.94
        ]
        
        new_zero_rates, new_forward_rates, arb_opps, ols_params = (
            self.analyzer.analyze_final_scenario(final_prices)
        )
        
        # Check if original prices were preserved
        assert_array_almost_equal(self.analyzer.bond_prices, np.array(self.base_prices))
        
        # Verify output shapes and values
        self.assertEqual(len(new_zero_rates), len(self.analyzer.payment_times))
        self.assertEqual(len(new_forward_rates), len(self.analyzer.payment_times) - 1)
        self.assertEqual(len(ols_params), 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)