import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Function to backtest forecasting methods
def backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes, time_horizon=38, num_simulations=10000):
    results = []

    # Function to fetch historical data
    def fetch_data(start, end):
        return yf.download(ticker_symbol, start=start, end=end)

    # Function to calculate log returns
    def calculate_log_returns(data):
        log_returns = np.log(data['Close'] / data['Close'].shift(1))
        log_returns.dropna(inplace=True)
        return log_returns

    # Main backtesting loop
    for size in historical_sizes:
        # Adjust start date for the historical data window
        adjusted_start_date = (pd.to_datetime(end_date) - pd.Timedelta(days=size)).strftime('%Y-%m-%d')
        historical_data = fetch_data(adjusted_start_date, end_date)
        
        # Skip if not enough data
        if len(historical_data) < size:
            print(f"Insufficient data for historical size {size} days.")
            continue

        # Calculate log returns
        log_returns = calculate_log_returns(historical_data)
        log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')

        # Monte Carlo Simulation
        initial_price = historical_data['Close'].iloc[-1]
        volatility = log_returns.std()
        vol_volatility = 0.4  # Volatility of volatility
        max_volatility = volatility * 2  # Cap volatility to prevent explosion

        np.random.seed(42)
        price_paths = np.zeros((time_horizon, num_simulations))
        price_paths[0] = initial_price

        for t in range(1, time_horizon):
            # Random shock for volatility with cap
            vol_shock = np.random.normal(0, vol_volatility, num_simulations)
            volatility = np.abs(volatility + vol_shock)
            volatility = np.minimum(volatility, max_volatility)

            # GBM component with adjusted volatility
            normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2,
                                              volatility / np.sqrt(252), num_simulations)

            # Update price paths
            price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)

        # Monte Carlo Forecast
        forecasted_price_mc = price_paths[-1].mean()

        # ARIMA-GARCH Forecasting
        arima_model = ARIMA(log_returns, order=(10, 0, 1))
        arima_result = arima_model.fit()
        arima_forecast = arima_result.forecast(steps=time_horizon)

        garch_model = arch_model(log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(update_freq=5, disp='off')
        garch_forecast = garch_result.forecast(horizon=time_horizon)
        forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100

        forecasted_log_return = arima_forecast.sum()
        forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)

        # Fetch actual price 30 days out for evaluation
        future_end_date = (pd.to_datetime(end_date) + pd.Timedelta(days=time_horizon)).strftime('%Y-%m-%d')
        future_data = fetch_data(end_date, future_end_date)

        if len(future_data['Close']) < time_horizon:
            print(f"Insufficient future data to evaluate forecasts for historical size {size} days.")
            continue

        actual_price_30d = future_data['Close'].iloc[-1]
        actual_direction = 1 if actual_price_30d > initial_price else -1

        # Evaluate Forecasts
        mc_direction = 1 if forecasted_price_mc > initial_price else -1
        arima_garch_direction = 1 if forecasted_price_arima_garch > initial_price else -1

        mc_percentage_error = abs((forecasted_price_mc - actual_price_30d) / actual_price_30d) * 100
        arima_garch_percentage_error = abs((forecasted_price_arima_garch - actual_price_30d) / actual_price_30d) * 100

        # Store results
        results.append({
            'Historical Size': size,
            'Forecast_Method': 'Monte Carlo',
            'Forecasted_Price': forecasted_price_mc,
            'Actual_Price': actual_price_30d,
            'Direction_Accuracy': mc_direction == actual_direction,
            'Percentage_Error': mc_percentage_error
        })

        results.append({
            'Historical Size': size,
            'Forecast_Method': 'ARIMA-GARCH',
            'Forecasted_Price': forecasted_price_arima_garch,
            'Actual_Price': actual_price_30d,
            'Direction_Accuracy': arima_garch_direction == actual_direction,
            'Percentage_Error': arima_garch_percentage_error
        })

        # Print results for the current backtest iteration
        print(f"Historical Size: {size} days")
        print(f"Monte Carlo: Forecasted Price = ${forecasted_price_mc:.2f}, "
              f"Actual Price = ${actual_price_30d:.2f}, "
              f"Direction Accuracy = {mc_direction == actual_direction}, "
              f"Percentage Error = {mc_percentage_error:.2f}%")
        print(f"ARIMA-GARCH: Forecasted Price = ${forecasted_price_arima_garch:.2f}, "
              f"Actual Price = ${actual_price_30d:.2f}, "
              f"Direction Accuracy = {arima_garch_direction == actual_direction}, "
              f"Percentage Error = {arima_garch_percentage_error:.2f}%")
        print()

    # Return full results as a DataFrame for further analysis
    return pd.DataFrame(results)

# Backtesting configuration
ticker_symbol = "LDOS"
start_date = "2023-04-01"
end_date = "2024-04-09"
historical_sizes = [250, 500, 750]  # Backtest with 1 year, 2 years, and 3 years of historical data
time_horizon = 30  # Forecast 30 days out

# Run backtesting
results_df = backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes, time_horizon)

# Print overall results
print(results_df)
