import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline
from sklearn.linear_model import LinearRegression

class BondAnalyzer:
    def __init__(self, libor_3m: float, libor_6m: float, bond_prices: list, scenario: str = 'base'):
        self.libor_3m = libor_3m
        self.libor_6m = libor_6m
        self.bond_prices = bond_prices
        self.scenario = scenario
        self.bonds_info = [
            {'label': 'Bond i', 'due_in': 36, 'coupon_pct': 0.04, 'coupon_interval': 3, 'principal_val': 100},
            {'label': 'Bond ii', 'due_in': 60, 'coupon_pct': 0.05, 'coupon_interval': 6, 'principal_val': 100},
            {'label': 'Bond iii', 'due_in': 114, 'coupon_pct': 0.05, 'coupon_interval': 6, 'principal_val': 100},
            {'label': 'Bond iv', 'due_in': 90, 'coupon_pct': 0.06, 'coupon_interval': 3, 'principal_val': 100},
            {'label': 'Bond v', 'due_in': 60, 'coupon_pct': 0.05, 'coupon_interval': 3, 'principal_val': 100},
            {'label': 'Bond vi', 'due_in': 360, 'coupon_pct': 0.03, 'coupon_interval': 12, 'principal_val': 100}
        ]

    def generate_payment_times(self) -> list:
        payment_times = set()
        for bond in self.bonds_info:
            months = np.arange(bond['coupon_interval'], bond['due_in'] + bond['coupon_interval'], bond['coupon_interval'])
            payment_times.update(months)
        return sorted(payment_times)

    def build_cashflow_matrix(self) -> np.ndarray:
        payment_times = self.generate_payment_times()
        num_payments = len(payment_times)
        month_indices_map = {month: index for index, month in enumerate(payment_times)}
        num_bonds = len(self.bonds_info)
        cashflow_mtx = np.zeros((num_bonds, num_payments))

        for i, bond in enumerate(self.bonds_info):
            coupon_val = bond['coupon_pct'] / (12 / bond['coupon_interval']) * bond['principal_val']
            months = np.arange(bond['coupon_interval'], bond['due_in'] + bond['coupon_interval'], bond['coupon_interval'])
            for mth in months:
                idx = month_indices_map[mth]
                if mth == bond['due_in']:
                    cashflow_mtx[i, idx] += coupon_val + bond['principal_val']
                else:
                    cashflow_mtx[i, idx] += coupon_val
        return cashflow_mtx

    def calibrate_zero_rates(self, cf_matrix: np.ndarray) -> np.ndarray:
        P = np.array(self.bond_prices)
        C_reduced = cf_matrix[:, :6]
        z, _, _, _ = np.linalg.lstsq(C_reduced.T, P, rcond=None)
        return z

    def calculate_forward_rates(self, zero_rates: np.ndarray) -> np.ndarray:
        forward_rates = []
        for i in range(1, len(zero_rates)):
            fwd_rate = (zero_rates[i-1] / zero_rates[i] - 1) / ((i - (i-1)) / 12)
            forward_rates.append(fwd_rate)
        return np.array(forward_rates)

    def calculate_swap_rate(self, zero_rates: np.ndarray) -> float:
        fixed_leg_pv = sum([z for z in zero_rates])
        floating_leg_pv = 1  # Assumed to be par in swap pricing
        return floating_leg_pv / fixed_leg_pv

    def price_receiver_swap(self, zero_rates: np.ndarray, notional: float = 1000000) -> float:
        fixed_leg_pv = sum([z for z in zero_rates])
        floating_leg_pv = notional  # Using par value for floating leg
        swap_value = fixed_leg_pv - floating_leg_pv
        return swap_value

    def check_arbitrage(self, zero_rates: np.ndarray) -> list:
        arbitrage_opportunities = []
        for i in range(1, len(zero_rates)):
            if zero_rates[i] < zero_rates[i-1]:
                arbitrage_opportunities.append(f"Arbitrage between months {i-1} and {i}")
        return arbitrage_opportunities

    def estimate_parameters_ols(self) -> np.ndarray:
        payment_times = self.generate_payment_times()
        num_payments = len(payment_times)
        X = np.vstack([np.ones(num_payments), payment_times]).T
        y = np.array(self.bond_prices)
        model = LinearRegression().fit(X, y)
        return model.coef_

    def analyze_final_scenario(self, final_prices: list) -> tuple:
        cashflow_mtx = self.build_cashflow_matrix()
        zero_rates = self.calibrate_zero_rates(cashflow_mtx)
        fwd_rates = self.calculate_forward_rates(zero_rates)
        swap_rate = self.calculate_swap_rate(zero_rates)
        return zero_rates, fwd_rates, swap_rate
