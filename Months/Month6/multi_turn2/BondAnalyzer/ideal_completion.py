import numpy as np
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression

class BondAnalyzer:
    def __init__(self, libor_3m: float, libor_6m: float, bond_prices: list, scenario: str = 'base'):
        self.libor_3m = libor_3m
        self.libor_6m = libor_6m
        self.bond_prices = bond_prices
        self.scenario = scenario

        self.bonds = self._initialize_bonds()
        self.payment_times = self.generate_payment_times()
        self.cashflow_matrix = self.build_cashflow_matrix()

    def _initialize_bonds(self):
        base_bonds = [
            {'maturity': 3, 'coupon_rate': 0.04, 'freq': 4},
            {'maturity': 5, 'coupon_rate': 0.045, 'freq': 2},
            {'maturity': 7, 'coupon_rate': 0.05, 'freq': 1},
            {'maturity': 10, 'coupon_rate': 0.055, 'freq': 2},
            {'maturity': 20, 'coupon_rate': 0.06, 'freq': 1},
            {'maturity': 30, 'coupon_rate': 0.065, 'freq': 4}
        ]
        jan_bonds = [
            {'maturity': 1, 'coupon_rate': 0.025, 'freq': 2},
            {'maturity': 2, 'coupon_rate': 0.0275, 'freq': 2},
            {'maturity': 3, 'coupon_rate': 0.03, 'freq': 4},
            {'maturity': 5, 'coupon_rate': 0.0325, 'freq': 2},
            {'maturity': 7, 'coupon_rate': 0.035, 'freq': 1},
            {'maturity': 10, 'coupon_rate': 0.0375, 'freq': 2},
            {'maturity': 15, 'coupon_rate': 0.04, 'freq': 1},
            {'maturity': 20, 'coupon_rate': 0.0425, 'freq': 1},
            {'maturity': 25, 'coupon_rate': 0.045, 'freq': 2},
            {'maturity': 30, 'coupon_rate': 0.0475, 'freq': 4}
        ]
        return jan_bonds if self.scenario == 'january' else base_bonds

    def generate_payment_times(self) -> list:
        payment_times = []
        for bond in self.bonds:
            freq = bond['freq']
            maturity = bond['maturity']
            times = [round(i / freq, 6) for i in range(1, maturity * freq + 1)]
            payment_times.extend(times)
        payment_times = sorted(set([t for t in payment_times if 0 < t <= 2.0]))
        return payment_times

    def build_cashflow_matrix(self) -> np.ndarray:
        num_bonds = len(self.bonds)
        num_times = len(self.payment_times)
        cf_matrix = np.zeros((num_bonds, num_times))

        for idx, bond in enumerate(self.bonds):
            freq = bond['freq']
            coupon_payment = (bond['coupon_rate'] * 100) / freq
            maturity = bond['maturity']
            bond_payment_times = [round(i / freq, 6) for i in range(1, maturity * freq + 1)]
            for t in bond_payment_times:
                if 0 < t <= 2.0:
                    col_idx = self.payment_times.index(t)
                    if abs(t - maturity) < 1e-6:
                        cf_matrix[idx, col_idx] = coupon_payment + 100.0  # Add principal to final payment
                    else:
                        cf_matrix[idx, col_idx] = coupon_payment
        return cf_matrix

    def calibrate_zero_rates(self, cf_matrix: np.ndarray) -> np.ndarray:
        bond_prices = np.array(self.bond_prices)
        num_times = len(self.payment_times)
        zero_rates = np.zeros(num_times)

        for i, t in enumerate(self.payment_times):
            def objective(r):
                pv = sum(cf_matrix[j, i] * np.exp(-r * t) for j in range(len(self.bonds)))
                return (pv - bond_prices[min(i, len(bond_prices) - 1)]) ** 2

            res = minimize(objective, x0=0.05, bounds=[(0.0001, 0.15)])
            zero_rates[i] = res.x[0]
        return zero_rates

    def estimate_parameters_ols(self) -> np.ndarray:
        zero_rates = self.calibrate_zero_rates(self.cashflow_matrix)
        times = np.array(self.payment_times).reshape(-1, 1)
        X = np.hstack((times ** 2, times))
        model = LinearRegression()
        model.fit(X, zero_rates)
        return np.array([model.intercept_, model.coef_[0], model.coef_[1]])

    def calculate_forward_rates(self, zero_rates: np.ndarray) -> np.ndarray:
        times = np.array(self.payment_times)
        forward_rates = []
        for i in range(1, len(times)):
            delta_t = times[i] - times[i - 1]
            if delta_t > 0:
                f_rate = (zero_rates[i] * times[i] - zero_rates[i - 1] * times[i - 1]) / delta_t
                f_rate = max(0.0001, min(f_rate, 0.15))
                forward_rates.append(f_rate)
        return np.array(forward_rates)

    def calculate_swap_rate(self, zero_rates: np.ndarray) -> float:
        discount_factors = np.exp(-zero_rates * np.array(self.payment_times))
        annuity = discount_factors.sum()
        swap_rate = (1 - discount_factors[-1]) / annuity if annuity != 0 else 0.0
        return max(0.0001, min(swap_rate, 0.15))

    def price_receiver_swap(self, zero_rates: np.ndarray, notional: float = 1000000) -> float:
        swap_rate = self.calculate_swap_rate(zero_rates)
        discount_factors = np.exp(-zero_rates * np.array(self.payment_times))
        fixed_leg = swap_rate * discount_factors.sum() * notional
        floating_leg = notional * (1 - discount_factors[-1])
        return floating_leg - fixed_leg

    def check_arbitrage(self, zero_rates: np.ndarray) -> list:
        arbitrage_opportunities = []
        for idx, bond in enumerate(self.bonds):
            market_price = self.bond_prices[min(idx, len(self.bond_prices) - 1)]
            model_price = sum(self.cashflow_matrix[idx, t_idx] * np.exp(-zero_rates[t_idx] * t)
                              for t_idx, t in enumerate(self.payment_times))
            price_diff = model_price - market_price
            if abs(price_diff) > 0.01:
                arbitrage_opportunities.append({
                    'bond_index': idx,
                    'action': 'buy' if price_diff > 0 else 'sell',
                    'price_difference': round(abs(price_diff), 4),
                    'market_price': round(market_price, 4),
                    'model_price': round(model_price, 4)
                })
        return arbitrage_opportunities

    def analyze_final_scenario(self, final_prices: list) -> tuple:
        original_prices = self.bond_prices.copy()
        self.bond_prices = final_prices
        zero_rates_final = self.calibrate_zero_rates(self.cashflow_matrix)
        forward_rates_final = self.calculate_forward_rates(zero_rates_final)
        swap_rate_final = self.calculate_swap_rate(zero_rates_final)
        arbitrage_opportunities = self.check_arbitrage(zero_rates_final)
        self.bond_prices = original_prices
        return zero_rates_final, forward_rates_final, swap_rate_final, arbitrage_opportunities

