import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm

def backtest_models(asset_symbol, start_date, end_date, rolling_windows):
    def fetch_data(symbol, start, end):
        return yf.download(symbol, start=start, end=end)
    
    def compute_log_returns(data):
        log_returns = np.log(data['Close'] / data['Close'].shift(1))
        log_returns.dropna(inplace=True)
        return log_returns

    results = []
    
    for window_size in rolling_windows:
        rolling_start = pd.to_datetime(end_date) - pd.Timedelta(days=window_size)
        rolling_end = pd.to_datetime(end_date)

        # Fetch training data
        training_data = fetch_data(asset_symbol, rolling_start.strftime('%Y-%m-%d'), rolling_end.strftime('%Y-%m-%d'))
        if len(training_data) < 60:
            continue  # Skip if not enough data for training
        
        daily_log_returns = compute_log_returns(training_data)
        starting_price = training_data['Close'].iloc[-1]
        
        # --- Monte Carlo Simulation ---
        forecast_horizon = 30
        simulations = 1000
        np.random.seed(24)
        simulated_prices = np.zeros((forecast_horizon, simulations))
        simulated_prices[0] = starting_price
        
        curr_volatility = daily_log_returns.std()
        vol_shock_intensity = 0.35
        peak_volatility = curr_volatility * 2
        
        for t in range(1, forecast_horizon):
            vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
            curr_volatility = np.abs(curr_volatility + vol_shock)
            curr_volatility = np.minimum(curr_volatility, peak_volatility)
            norm_returns = np.random.normal(daily_log_returns.mean() - (curr_volatility ** 2) / 2, curr_volatility / np.sqrt(252), simulations)
            simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)
        
        predicted_price_mc = simulated_prices[-1].mean()
        
        # --- ARIMA-GARCH ---
        arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
        arima_result = arima_model.fit()
        arima_prediction = arima_result.forecast(steps=30)
        
        garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(disp='off')
        garch_prediction = garch_result.forecast(horizon=30)
        predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100

        predicted_log_return = arima_prediction.sum()
        predicted_price_arima_garch = starting_price * np.exp(predicted_log_return / 100)

        # --- Actual Future Price ---
        test_start = rolling_end
        test_end = rolling_end + pd.Timedelta(days=30)
        future_data = fetch_data(asset_symbol, test_start.strftime('%Y-%m-%d'), test_end.strftime('%Y-%m-%d'))
        
        if len(future_data) == 0:
            continue

        actual_price_30d = future_data['Close'].iloc[-1]

        # --- Metrics ---
        direction_mc = np.sign(predicted_price_mc - starting_price) == np.sign(actual_price_30d - starting_price)
        direction_arima_garch = np.sign(predicted_price_arima_garch - starting_price) == np.sign(actual_price_30d - starting_price)
        
        percentage_error_mc = abs(predicted_price_mc - actual_price_30d) / actual_price_30d
        percentage_error_arima_garch = abs(predicted_price_arima_garch - actual_price_30d) / actual_price_30d
        
        results.append({
            'window': window_size,
            'predicted_mc': predicted_price_mc,
            'predicted_arima_garch': predicted_price_arima_garch,
            'actual_price': actual_price_30d,
            'direction_mc': direction_mc,
            'direction_arima_garch': direction_arima_garch,
            'percentage_error_mc': percentage_error_mc,
            'percentage_error_arima_garch': percentage_error_arima_garch
        })
        print(f"Window {window_size} days, Actual: ${actual_price_30d:.2f}, Monte Carlo: ${predicted_price_mc:.2f}, ARIMA-GARCH: ${predicted_price_arima_garch:.2f}")

    df_results = pd.DataFrame(results)
    print(df_results)
    print("\nSummary:")
    print(f"Monte Carlo Direction Accuracy: {df_results['direction_mc'].mean() * 100:.2f}%")
    print(f"ARIMA-GARCH Direction Accuracy: {df_results['direction_arima_garch'].mean() * 100:.2f}%")
    print(f"Monte Carlo Average Percentage Error: {df_results['percentage_error_mc'].mean() * 100:.2f}%")
    print(f"ARIMA-GARCH Average Percentage Error: {df_results['percentage_error_arima_garch'].mean() * 100:.2f}%")

backtest_models("GOOGL", "2023-01-01", "2024-01-30", [365, 730])
