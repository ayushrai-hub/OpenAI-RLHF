# ideal_completion.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline

class BondAnalyzer:
    def __init__(self, libor_3m, libor_6m, bond_prices):
        self.libor_3m = libor_3m
        self.libor_6m = libor_6m
        self.bond_prices = np.array(bond_prices)
        
        # Bond specifications
        self.bonds = [
            {'maturity': 1.0, 'coupon': 0.04, 'freq': 4},  # Quarterly
            {'maturity': 1.0, 'coupon': 0.05, 'freq': 2},  # Semi-annual
            {'maturity': 1.5, 'coupon': 0.05, 'freq': 2},  # Semi-annual
            {'maturity': 1.5, 'coupon': 0.06, 'freq': 4},  # Quarterly
            {'maturity': 2.0, 'coupon': 0.05, 'freq': 4},  # Quarterly
            {'maturity': 2.0, 'coupon': 0.03, 'freq': 1}   # Annual
        ]
        
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
        """Calibrate zero rates"""
        def objective(params):
            beta0, beta1, beta2, tau = params
            times = np.array(self.payment_times)
            rates = (beta0 + 
                    beta1 * (1 - np.exp(-times/tau))/(times/tau) +
                    beta2 * ((1 - np.exp(-times/tau))/(times/tau) - np.exp(-times/tau)))
            
            df = np.exp(-rates * times)
            model_prices = cf_matrix @ df
            return np.sum((model_prices - self.bond_prices)**2)
        
        initial_params = [
            self.libor_3m,  # beta0
            0.01,          # beta1
            0.01,          # beta2
            1.0            # tau
        ]
        
        bounds = [
            (self.libor_3m * 0.8, self.libor_3m * 1.2),
            (0.0, 0.05),
            (0.0, 0.05),
            (0.1, 5.0)
        ]
        
        result = minimize(
            objective,
            initial_params,
            method='SLSQP',
            bounds=bounds,
            options={'ftol': 1e-8}
        )
        
        if not result.success:
            raise ValueError("Rate calibration failed")
            
        beta0, beta1, beta2, tau = result.x
        times = np.array(self.payment_times)
        rates = (beta0 + 
                beta1 * (1 - np.exp(-times/tau))/(times/tau) +
                beta2 * ((1 - np.exp(-times/tau))/(times/tau) - np.exp(-times/tau)))
        
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

    def price_floating_bond(self, zero_rates):
        """Price floating rate bond"""
        times = np.array(self.payment_times)
        df = np.exp(-zero_rates * times)
        
        # Initial value is par
        price = 100.0 * df[-1]  # Discounted principal
        
        # Calculate floating payments
        payment_times = times[times <= 2.0]
        payment_df = df[times <= 2.0]
        
        for i in range(len(payment_times)-1):
            # Forward LIBOR rate
            t1, t2 = payment_times[i], payment_times[i+1]
            df1, df2 = payment_df[i], payment_df[i+1]
            forward_libor = (df1/df2 - 1) * 2  # Annualized
            
            # Semi-annual payment
            payment = forward_libor * 100 * 0.5
            price += payment * df1
        
        # First known payment
        price += self.libor_6m * 100 * 0.5 * df[0]
        
        return price

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
    # Market data
    LIBOR_3M = 0.01472717
    LIBOR_6M = 0.01893706
    bond_prices = [
        102.33689177,
        104.80430234,
        105.1615306,
        105.6581905,
        104.028999992,
        101.82604116
    ]
    
    analyzer = BondAnalyzer(LIBOR_3M, LIBOR_6M, bond_prices)
    
    # Execute analysis
    cf_matrix = analyzer.build_cashflow_matrix()
    zero_rates = analyzer.calibrate_zero_rates(cf_matrix)
    forward_rates = analyzer.calculate_forward_rates(zero_rates)
    frn_price = analyzer.price_floating_bond(zero_rates)
    swap_rate = analyzer.calculate_swap_rate(zero_rates)
    
    # Print results
    print("Cashflow Matrix:")
    print(cf_matrix)
    
    print("\nZero Rates:")
    for t, r in zip(analyzer.payment_times, zero_rates):
        print(f"{t:.2f}Y: {r*100:.4f}%")
    
    print("\nForward Rates:")
    for i, r in enumerate(forward_rates):
        print(f"{analyzer.payment_times[i]:.2f}Y-{analyzer.payment_times[i+1]:.2f}Y: "
              f"{r*100:.4f}%")
    
    print(f"\nFloating Rate Bond Price: {frn_price:.4f}")
    print(f"Swap Rate: {swap_rate*100:.4f}%")
    
    # Plot results
    analyzer.plot_results(zero_rates, forward_rates, swap_rate)

if __name__ == "__main__":
    main()
