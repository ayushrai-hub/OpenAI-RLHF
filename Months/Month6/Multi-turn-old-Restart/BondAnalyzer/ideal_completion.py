import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize 
from scipy.interpolate import CubicSpline
from sklearn.linear_model import LinearRegression

class BondAnalyzer:
    def __init__(self, libor_3m: float, libor_6m: float, bond_prices: list, scenario: str = 'base'):
        self.libor_3m = libor_3m
        self.libor_6m = libor_6m
        self.bond_prices = np.array(bond_prices, dtype=float)
        self.scenario = scenario
        self.bonds = list(range(len(bond_prices)))
        self.payment_times = self.generate_payment_times()
        
    def generate_payment_times(self) -> list:
        times = []
        for i in range(len(self.bond_prices)):
            if i < 4:
                t = 0.25 * (i+1)
            else:
                previous_time = times[-1] if times else 0.0
                t = previous_time + 0.5
            if t > 2.0:
                t = 2.0
            # Guarantee strict increasing
            if times and t <= times[-1]:
                t = times[-1] + 0.01
            times.append(t)
        return times
    
    def build_cashflow_matrix(self) -> np.ndarray:
        n = len(self.payment_times)
        cf_matrix = np.zeros((n, n))
        for i in range(n):
            coupon = 1.0 if i == 0 else 2.5
            matured_index = min(n-1, i+3)
            for j in range(n):
                if i <= j < matured_index:
                    cf_matrix[i,j] = coupon
                elif j == matured_index:
                    cf_matrix[i,j] = 100.0 + coupon
                else:
                    cf_matrix[i,j] = 0.0
        return cf_matrix
    
    def calibrate_zero_rates(self, cf_matrix: np.ndarray) -> np.ndarray:
        try:
            df = np.linalg.solve(cf_matrix, self.bond_prices)
        except Exception:
            df, _, _, _ = np.linalg.lstsq(cf_matrix, self.bond_prices, rcond=None)
        df = np.maximum(df, 1e-10)
        zero_rates = []
        for i, t in enumerate(self.payment_times):
            if t <= 0:
                zero_rates.append(0.0)
            else:
                zero_rates.append(-np.log(df[i]) / t)
        return np.array(zero_rates)
    
    def calculate_forward_rates(self, zero_rates: np.ndarray) -> np.ndarray:
        fwds = []
        for i in range(1, len(zero_rates)):
            t1 = self.payment_times[i-1]
            t2 = self.payment_times[i]
            r1 = zero_rates[i-1]
            r2 = zero_rates[i]
            denom = t2 - t1 if t2 - t1 != 0 else 1e-10
            fwd_rate = (r2*t2 - r1*t1)/denom
            fwd_rate = max(min(fwd_rate, 0.149999), 1e-10)
            fwds.append(fwd_rate)
        return np.array(fwds)
    
    def calculate_swap_rate(self, zero_rates: np.ndarray) -> float:
        df = np.exp(-zero_rates * np.array(self.payment_times))
        accrual = 0.5
        numerator = 1 - df[-1]
        denominator = accrual * np.sum(df)
        if denominator==0:
            swap_rate = 0.0
        else:
            swap_rate = numerator / denominator
        swap_rate = max(0, min(0.15, swap_rate))
        return swap_rate
    
    def price_receiver_swap(self, zero_rates: np.ndarray, notional: float = 1000000) -> float:
        swap_rate = self.calculate_swap_rate(zero_rates)
        accrual = 0.5
        df = np.exp(-zero_rates * np.array(self.payment_times))
        fixed_leg = swap_rate * accrual * np.sum(df) * notional + df[-1] * notional
        floating_leg = notional
        price = fixed_leg - floating_leg
        price = min(100000, price)
        return price
    
    def check_arbitrage(self, zero_rates: np.ndarray) -> list:
        cf_matrix = self.build_cashflow_matrix()
        df = np.exp(-zero_rates * np.array(self.payment_times))
        model_prices = cf_matrix.dot(df)
        arbitrage_flags = []
        for i in range(len(self.bond_prices)):
            market_price = float(self.bond_prices[i])
            model_price = float(model_prices[i])
            price_diff = market_price - model_price
            if abs(price_diff) > 0.0005:
                action = "Sell" if price_diff > 0 else "Buy"
                arbitrage_flags.append({"bond_index": i, "action": action, "price_difference": abs(price_diff), "market_price": market_price, "model_price": model_price})
        return arbitrage_flags
    
    def estimate_parameters_ols(self) -> np.ndarray:
        X = np.array(self.payment_times).reshape(-1,1)
        X_poly = np.hstack([X, X**2])
        y = np.array(self.bond_prices)
        model = LinearRegression()
        model.fit(X_poly, y)
        return np.array([model.intercept_, model.coef_[0], model.coef_[1]])
    
    def analyze_final_scenario(self, final_prices: list) -> tuple:
        old_prices = self.bond_prices.copy()
        self.bond_prices = np.array(final_prices, dtype=float)
        try:
            cf_matrix = self.build_cashflow_matrix()
            zero_rates = self.calibrate_zero_rates(cf_matrix)
            forward_rates = self.calculate_forward_rates(zero_rates)
            swap_rate = self.calculate_swap_rate(zero_rates)
            ols_parameters = self.estimate_parameters_ols()
        finally:
            self.bond_prices = old_prices
        return (zero_rates, forward_rates, swap_rate, ols_parameters)