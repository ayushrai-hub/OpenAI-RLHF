import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from datetime import timedelta

# Backtesting function
def backtest_predictions(asset_symbol, initial_start, final_end, window_sizes, forecast_horizon=38, simulations=10000):
    
    results = []

    # Fetch complete dataset once
    complete_data = yf.download(asset_symbol, start=initial_start, end=final_end)
    
    for window in window_sizes:
        print(f"\nBacktesting with historical window: {window} days")
        
        # Compute start and end dates for each historical window
        test_start_date = pd.to_datetime(final_end) - pd.Timedelta(days=window + forecast_horizon)
        test_end_date = pd.to_datetime(final_end) - pd.Timedelta(days=forecast_horizon)

        # Extract historical data window
        historical_data = complete_data.loc[test_start_date:test_end_date].copy()
        
        # Check if we have sufficient data for backtesting
        if historical_data.empty or len(historical_data) < window:
            print("Insufficient data for this window. Skipping.")
            continue
        
        # Calculate daily log returns
        daily_log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1)).dropna()
        daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')

        # Monte Carlo Simulation
        np.random.seed(24)
        curr_volatility = daily_log_returns.std()
        peak_volatility = curr_volatility * 2
        
        monte_carlo_prices = np.zeros((forecast_horizon, simulations))
        monte_carlo_prices[0] = historical_data['Close'].iloc[-1]
        
        for t in range(1, forecast_horizon):
            vol_shock = np.random.normal(0, 0.35, simulations)
            curr_volatility = np.abs(curr_volatility + vol_shock)
            curr_volatility = np.minimum(curr_volatility, peak_volatility)
            
            norm_returns = np.random.normal(daily_log_returns.mean() - (curr_volatility ** 2) / 2, 
                                            curr_volatility / np.sqrt(252), simulations)
            
            monte_carlo_prices[t] = monte_carlo_prices[t - 1] * np.exp(norm_returns)
        
        predicted_price_mc = monte_carlo_prices[-1].mean()
        
        # ARIMA-GARCH Model
        arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
        arima_result = arima_model.fit()
        arima_pred = arima_result.forecast(steps=forecast_horizon)

        garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(disp='off')
        garch_pred_var = garch_result.forecast(horizon=forecast_horizon).variance.iloc[-1].values
        garch_pred_volatility = np.sqrt(garch_pred_var) / 100
        
        predicted_log_return = arima_pred.sum()
        predicted_price_arima_garch = historical_data['Close'].iloc[-1] * np.exp(predicted_log_return / 100)

        # Actual price after forecast_horizon days
        actual_price_date = pd.to_datetime(test_end_date) + timedelta(days=forecast_horizon)
        
        if actual_price_date > pd.to_datetime(final_end):
            print("Insufficient actual data for comparison. Skipping")
            continue
        
        actual_price = complete_data.loc[actual_price_date.strftime('%Y-%m-%d'), 'Close']

        # Check direction accuracy
        mc_direction_correct = (predicted_price_mc - historical_data['Close'].iloc[-1]) * (actual_price - historical_data['Close'].iloc[-1]) > 0
        ag_direction_correct = (predicted_price_arima_garch - historical_data['Close'].iloc[-1]) * (actual_price - historical_data['Close'].iloc[-1]) > 0
        
        # Percentage error
        mc_pct_error = abs((predicted_price_mc - actual_price) / actual_price) * 100
        ag_pct_error = abs((predicted_price_arima_garch - actual_price) / actual_price) * 100
        
        results.append({
            "Window Size (days)": window,
            "Actual Price": actual_price,
            "MC Predicted Price": predicted_price_mc,
            "ARIMA-GARCH Predicted Price": predicted_price_arima_garch,
            "MC Direction Correct": mc_direction_correct,
            "ARIMA-GARCH Direction Correct": ag_direction_correct,
            "MC Percentage Error": mc_pct_error,
            "ARIMA-GARCH Percentage Error": ag_pct_error
        })

    # Results DataFrame
    results_df = pd.DataFrame(results)
    print("\nBacktest Results:")
    print(results_df)
    
    # Plotting percentage errors
    plt.figure(figsize=(14, 7))
    plt.plot(results_df["Window Size (days)"], results_df["MC Percentage Error"], marker='o', label='Monte Carlo % Error')
    plt.plot(results_df["Window Size (days)"], results_df["ARIMA-GARCH Percentage Error"], marker='x', label='ARIMA-GARCH % Error')
    plt.xlabel("Historical Window Size (Days)")
    plt.ylabel("Percentage Error (%)")
    plt.title(f"Prediction Error over different Historical Windows ({asset_symbol})")
    plt.legend()
    plt.grid(True)
    plt.show()

# Execute backtesting
backtest_predictions(
    asset_symbol="GOOGL", 
    initial_start="2022-01-01", 
    final_end="2024-01-30", 
    window_sizes=[120, 180, 240, 300, 365, 450, 540]
)
