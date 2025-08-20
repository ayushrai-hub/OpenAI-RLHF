import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline
from sklearn.linear_model import LinearRegression

class BondAnalyzer:
    def __init__(self, libor_3m, libor_6m, bond_prices, scenario='base'):
        self.libor_3m = libor_3m
        self.libor_6m = libor_6m
        self.bond_prices = np.array(bond_prices)
        self.scenario = scenario
        
        # Bond specifications
        self.bonds = [
            {'maturity': 1.0, 'coupon': 0.04, 'freq': 4},  # Quarterly
            {'maturity': 1.0, 'coupon': 0.05, 'freq': 2},  # Semi-annual
            {'maturity': 1.5, 'coupon': 0.05, 'freq': 2},  # Semi-annual
            {'maturity': 1.5, 'coupon': 0.06, 'freq': 4},  # Quarterly
            {'maturity': 2.0, 'coupon': 0.05, 'freq': 4},  # Quarterly
            {'maturity': 2.0, 'coupon': 0.03, 'freq': 1}   # Annual
        ]
        
        # Add zero-coupon bonds for January scenario
        if scenario == 'january':
            self.bonds.extend([
                {'maturity': 0.5, 'coupon': 0.0, 'freq': 2},  # 6-month zero
                {'maturity': 1.0, 'coupon': 0.0, 'freq': 2},  # 1-year zero
                {'maturity': 1.5, 'coupon': 0.0, 'freq': 2},  # 18-month zero
                {'maturity': 2.0, 'coupon': 0.0, 'freq': 2}   # 2-year zero
            ])
        
        # Generate payment schedule
        self.payment_times = self.generate_payment_times()

    def generate_payment_times(self):
        """Generate unique payment times"""
        times = set()
        for bond in self.bonds:
            freq = bond['freq']
            maturity = bond['maturity']
            payments = np.arange(1/freq, maturity + 1e-10, 1/freq)
            times.update(payments)
        return sorted(list(times))

    def build_cashflow_matrix(self):
        """Build cashflow matrix"""
        n_bonds = len(self.bonds)
        n_times = len(self.payment_times)
        cf_matrix = np.zeros((n_bonds, n_times))
        
        for i, bond in enumerate(self.bonds):
            period = 1.0/bond['freq']
            coupon = bond['coupon'] * 100 / bond['freq']
            
            for j, t in enumerate(self.payment_times):
                if abs(t % period) < 1e-10 and t <= bond['maturity']:
                    cf_matrix[i, j] = coupon
                    if abs(t - bond['maturity']) < 1e-10:
                        cf_matrix[i, j] += 100
                        
        return cf_matrix

    def calibrate_zero_rates(self, cf_matrix):
        """
        Calibrate zero rates using an improved optimization approach with better bounds handling
        and warning suppression.
        """
        import warnings
        from contextlib import contextmanager
        
        @contextmanager
        def warn_handler():
            """Context manager to temporarily suppress specific RuntimeWarnings"""
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=RuntimeWarning, 
                                    message='Values in x were outside bounds during a minimize step')
                yield

        def objective(params):
            """
            Objective function with improved parameter handling and bounds enforcement
            """
            # Safely transform parameters within bounds
            beta0 = np.clip(np.exp(params[0]), 0.001, 0.15)  # 0.1% to 15%
            beta1 = np.clip(params[1], -0.02, 0.02)
            beta2 = np.clip(params[2], -0.02, 0.02)
            tau = np.clip(np.exp(params[3]), 0.5, 5.0)
            
            times = np.array(self.payment_times)
            
            # Calculate rates with safe bounds
            rates = np.maximum(0.001, beta0 + 
                    beta1 * (1 - np.exp(-times/tau))/(times/tau) +
                    beta2 * ((1 - np.exp(-times/tau))/(times/tau) - np.exp(-times/tau)))
            
            # Ensure rates stay within reasonable bounds
            rates = np.clip(rates, 0.001, 0.15)
            
            df = np.exp(-rates * times)
            model_prices = cf_matrix @ df
            
            # Add penalties for boundary violations
            bounds_penalty = 1000 * (
                np.sum(np.maximum(0, -rates)) +  # Penalty for negative rates
                np.sum(np.maximum(0, rates - 0.15))  # Penalty for too high rates
            )
            
            # L2 regularization with reduced weight
            regularization = 0.05 * np.sum(params**2)
            
            return (np.sum((model_prices - self.bond_prices)**2) + 
                    bounds_penalty + regularization)
        
        # Adjusted bounds with wider ranges for better convergence
        bounds = [
            (np.log(0.001), np.log(0.15)),  # log(beta0)
            (-0.02, 0.02),                   # beta1
            (-0.02, 0.02),                   # beta2
            (np.log(0.5), np.log(5.0))       # log(tau)
        ]
        
        # Multiple starting points with more diverse initial guesses
        starting_points = [
            [np.log(self.libor_3m), 0.001, 0.001, np.log(1.0)],
            [np.log(self.libor_6m), 0.002, -0.001, np.log(2.0)],
            [np.log(0.02), 0.0, 0.0, np.log(1.5)],
            [np.log(0.01), -0.001, 0.001, np.log(3.0)]
        ]
        
        best_result = None
        min_objective = float('inf')
        
        # Try optimization with different starting points
        with warn_handler():
            for initial_params in starting_points:
                try:
                    result = minimize(
                        objective,
                        initial_params,
                        method='SLSQP',
                        bounds=bounds,
                        options={
                            'ftol': 1e-10,
                            'maxiter': 1000,
                            'disp': False
                        }
                    )
                    
                    if result.fun < min_objective and result.success:
                        min_objective = result.fun
                        best_result = result
                        
                except Exception as e:
                    print(f"Optimization attempt failed: {str(e)}")
                    continue
        
        if best_result is None:
            raise ValueError("Rate calibration failed for all starting points")
        
        # Transform parameters back and ensure they're within bounds
        beta0 = np.clip(np.exp(best_result.x[0]), 0.001, 0.15)
        beta1 = np.clip(best_result.x[1], -0.02, 0.02)
        beta2 = np.clip(best_result.x[2], -0.02, 0.02)
        tau = np.clip(np.exp(best_result.x[3]), 0.5, 5.0)
        
        times = np.array(self.payment_times)
        rates = np.clip(
            beta0 + 
            beta1 * (1 - np.exp(-times/tau))/(times/tau) +
            beta2 * ((1 - np.exp(-times/tau))/(times/tau) - np.exp(-times/tau)),
            0.001, 0.15
        )
        
        # Validation
        if not np.all(np.isfinite(rates)):
            raise ValueError("Non-finite rates detected in calibration result")
        
        return rates

    def calculate_forward_rates(self, zero_rates):
        """Calculate forward rates"""
        times = np.array(self.payment_times)
        cs = CubicSpline(times, zero_rates)
        forwards = []
        
        for i in range(len(times)-1):
            t1, t2 = times[i], times[i+1]
            dt = t2 - t1
            r1, r2 = zero_rates[i], zero_rates[i+1]
            fwd = (r2 * t2 - r1 * t1) / dt
            forwards.append(fwd)
            
        return np.array(forwards)

    def calculate_swap_rate(self, zero_rates):
        """Calculate swap rate"""
        times = np.array(self.payment_times)
        df = np.exp(-zero_rates * times)
        
        # Semi-annual fixed leg payments
        fixed_times = times[times <= 2.0]
        fixed_df = df[times <= 2.0]
        fixed_leg_pv01 = sum(fixed_df[::2]) * 0.5
        
        # Floating leg value
        float_leg_value = 100 * (1 - df[np.searchsorted(times, 2.0)-1])
        
        return float_leg_value / (100 * fixed_leg_pv01)

    def price_receiver_swap(self, zero_rates, notional=1000000):
        """Price a receiver swap"""
        times = np.array(self.payment_times)
        df = np.exp(-zero_rates * times)
        
        # Fixed leg (receive fixed)
        fixed_rate = 0.02  # 2% fixed rate
        payment_times = times[times <= 2.0][::2]  # Semi-annual payments
        fixed_payments = fixed_rate * notional * 0.5
        fixed_leg = sum(fixed_payments * df[::2])
        
        # Floating leg (pay floating)
        float_leg = notional * (1 - df[np.searchsorted(times, 2.0)-1])
        
        return fixed_leg - float_leg

    def check_arbitrage(self, zero_rates):
        # Add transaction costs
        transaction_cost = 0.0005  # 5 bps
        
        times = np.array(self.payment_times)
        df = np.exp(-zero_rates * times)
        cf_matrix = self.build_cashflow_matrix()
        model_prices = cf_matrix @ df
        
        price_diffs = self.bond_prices - model_prices
        arbitrage_opportunities = []
        
        for i, diff in enumerate(price_diffs):
            # Only flag opportunities beyond transaction costs
            if abs(diff) > transaction_cost:
                action = "Buy" if diff < 0 else "Sell"
                arbitrage_opportunities.append({
                    'bond_index': i,
                    'action': action,
                    'price_difference': abs(diff),
                    'market_price': self.bond_prices[i],
                    'model_price': model_prices[i],
                    'profit_after_costs': abs(diff) - transaction_cost
                })
        
        return arbitrage_opportunities

    def estimate_parameters_ols(self):
        # Scale parameters to be in percentage terms
        maturities = np.array([bond['maturity'] for bond in self.bonds])
        log_prices = np.log(self.bond_prices / 100)
        
        # Scale factors for numerical stability
        scale = 0.01  # Convert to percentage
        
        X = np.column_stack([
            maturities * scale,
            (1 - np.exp(-maturities)) / maturities * scale,
            ((1 - np.exp(-maturities)) / maturities - np.exp(-maturities)) * scale
        ])
        
        model = LinearRegression(fit_intercept=False)
        model.fit(X, -log_prices)
        
        return model.coef_ * scale  # Scale back to decimal

    def analyze_final_scenario(self, new_prices):
        """Analyze final scenario with enhanced validation"""
        original_prices = self.bond_prices.copy()
        self.bond_prices = np.array(new_prices)
        
        try:
            # Calculate zero rates with new prices
            cf_matrix = self.build_cashflow_matrix()
            new_zero_rates = self.calibrate_zero_rates(cf_matrix)
            new_forward_rates = self.calculate_forward_rates(new_zero_rates)
            ols_params = self.estimate_parameters_ols()
            
            # Calculate theoretical prices
            maturities = np.array([bond['maturity'] for bond in self.bonds])
            theoretical_rates = (ols_params[0] * maturities + 
                            ols_params[1] * (1 - np.exp(-maturities)) / maturities +
                            ols_params[2] * ((1 - np.exp(-maturities)) / maturities - np.exp(-maturities)))
            
            theoretical_prices = 100 * np.exp(-theoretical_rates * maturities)
            
            # Check for arbitrage opportunities
            arbitrage_opps = []
            price_diffs = self.bond_prices - theoretical_prices
            
            for i, diff in enumerate(price_diffs):
                if abs(diff) > 0.01:  # 1 basis point threshold
                    action = "Buy" if diff < 0 else "Sell"
                    arbitrage_opps.append({
                        'bond_index': i,
                        'action': action,
                        'price_difference': abs(diff),
                        'market_price': self.bond_prices[i],
                        'theoretical_price': theoretical_prices[i],
                        'maturity': self.bonds[i]['maturity'],
                        'coupon': self.bonds[i]['coupon']
                    })
            
        finally:
            # Ensure we restore original prices even if there's an error
            self.bond_prices = original_prices
        
        return new_zero_rates, new_forward_rates, arbitrage_opps, ols_params

    def plot_results(self, zero_rates, forward_rates, swap_rate):
        """Plot zero rates and forward rates"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Zero rates plot
        ax1.plot(self.payment_times, zero_rates * 100, 'b-o', label='Zero Rates')
        ax1.scatter([0.25, 0.5], [self.libor_3m * 100, self.libor_6m * 100],
                   c='red', label='LIBOR Rates')
        ax1.set_ylabel('Rate (%)')
        ax1.set_title('Zero Rates Curve')
        ax1.grid(True)
        ax1.legend()
        
        # Forward rates plot
        ax2.plot(self.payment_times[:-1], forward_rates * 100, 'g-o', 
                label='Forward Rates')
        ax2.axhline(y=swap_rate * 100, color='r', linestyle='--',
                    label=f'Swap Rate ({swap_rate*100:.2f}%)')
        ax2.set_xlabel('Time (Years)')
        ax2.set_ylabel('Rate (%)')
        ax2.set_title('Forward Rates and Swap Rate')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()

def main():
    # Base scenario
    LIBOR_3M = 0.01472717
    LIBOR_6M = 0.01893706
    base_prices = [
        102.33689177,
        104.80430234,
        105.1615306,
        105.6581905,
        104.028999992,
        101.82604116
    ]
    
    # January 30, 2020 scenario
    january_prices = base_prices + [
        99.05,    # 6-month zero
        97.82,    # 1-year zero
        96.43,    # 18-month zero
        95.01     # 2-year zero
    ]
    
    # Final scenario prices
    final_prices = [
        102.45,
        104.92,
        105.28,
        105.78,
        104.15,
        101.94
    ]
    
    # Base scenario analysis
    print("=== Base Scenario Analysis ===")
    base_analyzer = BondAnalyzer(LIBOR_3M, LIBOR_6M, base_prices)
    cf_matrix = base_analyzer.build_cashflow_matrix()
    zero_rates = base_analyzer.calibrate_zero_rates(cf_matrix)
    forward_rates = base_analyzer.calculate_forward_rates(zero_rates)
    swap_rate = base_analyzer.calculate_swap_rate(zero_rates)
    base_analyzer.plot_results(zero_rates, forward_rates, swap_rate)
    
    # January scenario analysis
    print("\n=== January 30, 2020 Scenario Analysis ===")
    jan_analyzer = BondAnalyzer(LIBOR_3M, LIBOR_6M, january_prices, 'january')
    jan_cf_matrix = jan_analyzer.build_cashflow_matrix()
    jan_zero_rates = jan_analyzer.calibrate_zero_rates(jan_cf_matrix)
    jan_forward_rates = jan_analyzer.calculate_forward_rates(jan_zero_rates)
    
    # Calculate receiver swap price
    swap_price = jan_analyzer.price_receiver_swap(jan_zero_rates)
    print(f"Receiver Swap Price: ${swap_price:,.2f}")
    
    # Check for arbitrage opportunities
    arb_opps = jan_analyzer.check_arbitrage(jan_zero_rates)
    if arb_opps:
        print("\nArbitrage Opportunities Found:")
        for opp in arb_opps:
            print(f"Bond {opp['bond_index']}: {opp['action']} "
                  f"(Difference: {opp['price_difference']:.4f})")
    
    # Final scenario analysis
    print("\n=== Final Scenario Analysis ===")
    # Estimate parameters using OLS and analyze final scenario
    new_zero_rates, new_forward_rates, final_arb_opps, ols_params = (
        base_analyzer.analyze_final_scenario(final_prices)
    )
    
    print("OLS Parameters:")
    print(f"Beta0 (Level): {ols_params[0]:.6f}")
    print(f"Beta1 (Slope): {ols_params[1]:.6f}")
    print(f"Beta2 (Curvature): {ols_params[2]:.6f}")
    
    print("\nFinal Scenario Arbitrage Opportunities:")
    for opp in final_arb_opps:
        print(f"Bond {opp['bond_index']}: {opp['action']} "
              f"(Difference: {opp['price_difference']:.4f})")
        print(f"  Market Price: {opp['market_price']:.4f}")
        print(f"  Model Price: {opp['theoretical_price']:.4f}")
    
        print("\nZero Rates:")
    for t, r in zip(base_analyzer.payment_times, zero_rates):
        print(f"{t:.2f}Y: {r*100:.4f}%")
    
    print("\nForward Rates:")
    for i, r in enumerate(forward_rates):
        print(f"{base_analyzer.payment_times[i]:.2f}Y-{base_analyzer.payment_times[i+1]:.2f}Y: {r*100:.4f}%")

    # Plot comparison of all scenarios
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Zero rates comparison
    ax1.plot(base_analyzer.payment_times, zero_rates * 100, 'b-o', 
             label='Base Scenario')
    ax1.plot(jan_analyzer.payment_times, jan_zero_rates * 100, 'g-o', 
             label='January Scenario')
    ax1.plot(base_analyzer.payment_times, new_zero_rates * 100, 'r-o', 
             label='Final Scenario')
    ax1.set_ylabel('Rate (%)')
    ax1.set_title('Zero Rates Comparison')
    ax1.grid(True)
    ax1.legend()
    
    # Forward rates comparison
    ax2.plot(base_analyzer.payment_times[:-1], forward_rates * 100, 'b-o', 
             label='Base Scenario')
    ax2.plot(jan_analyzer.payment_times[:-1], jan_forward_rates * 100, 'g-o', 
             label='January Scenario')
    ax2.plot(base_analyzer.payment_times[:-1], new_forward_rates * 100, 'r-o', 
             label='Final Scenario')
    ax2.set_xlabel('Time (Years)')
    ax2.set_ylabel('Rate (%)')
    ax2.set_title('Forward Rates Comparison')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()