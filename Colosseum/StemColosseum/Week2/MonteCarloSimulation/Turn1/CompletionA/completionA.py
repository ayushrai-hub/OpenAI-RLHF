import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Function to fetch historical data
def fetch_data(ticker_symbol, start, end):
    return yf.download(ticker_symbol, start=start, end=end)

# Function to calculate log returns
def calculate_log_returns(data):
    log_returns = np.log(data['Close'] / data['Close'].shift(1))
    log_returns.dropna(inplace=True)
    return log_returns

# Function for Monte Carlo simulation forecasting
def monte_carlo_simulation(log_returns, initial_price, time_horizon, num_simulations=10000):
    np.random.seed(42)
    price_paths = np.zeros((time_horizon, num_simulations))
    price_paths[0] = initial_price

    volatility = log_returns.std()
    vol_volatility = 0.4
    max_volatility = volatility * 2

    for t in range(1, time_horizon):
        vol_shock = np.random.normal(0, vol_volatility, num_simulations)
        volatility = np.abs(volatility + vol_shock)
        volatility = np.minimum(volatility, max_volatility)

        normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2, volatility / np.sqrt(252),
                                          num_simulations)
        price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)

    forecasted_price = price_paths[-1].mean()
    sorted_prices = np.sort(price_paths[-1])
    confidence_level_mc = 0.95
    VaR_mc = np.percentile(sorted_prices, (1 - confidence_level_mc) * 100)
    ES_mc = sorted_prices[sorted_prices <= VaR_mc].mean()

    return forecasted_price, VaR_mc, ES_mc

# Function for ARIMA-GARCH forecasting
def arima_garch_forecasting(log_returns, initial_price, time_horizon):
    # ARIMA model for returns prediction
    arima_model = ARIMA(log_returns, order=(10, 0, 1))
    arima_result = arima_model.fit()
    arima_forecast = arima_result.forecast(steps=time_horizon)

    # GARCH model for volatility estimation
    garch_model = arch_model(log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
    garch_result = garch_model.fit(update_freq=5, disp='off')
    garch_forecast = garch_result.forecast(horizon=time_horizon)

    forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100
    forecasted_log_return = arima_forecast.sum()
    forecasted_price = initial_price * np.exp(forecasted_log_return / 100)

    confidence_level = 0.95
    z_score = norm.ppf(confidence_level)
    VaR_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1]))
    ES_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1] / (1 - confidence_level)))

    return forecasted_price, VaR_arima_garch, ES_arima_garch

# Function for backtesting the forecasting models
def backtest_forecasting(ticker_symbol, historical_sizes, end_date, time_horizon=30):
    for size in historical_sizes:
        start_date = (pd.to_datetime(end_date) - pd.Timedelta(days=size)).strftime('%Y-%m-%d')
        
        # Fetch historical data
        historical_data = fetch_data(ticker_symbol, start_date, end_date)
        log_returns = calculate_log_returns(historical_data)

        # Monte Carlo forecast
        mc_forecast, VaR_mc, ES_mc = monte_carlo_simulation(log_returns, historical_data['Close'].iloc[-1], time_horizon)
        print(f"Monte Carlo forecast based on {size} days of historical data: ${mc_forecast:.2f}")

        # ARIMA-GARCH forecast
        arima_garch_forecast, VaR_arima_garch, ES_arima_garch = arima_garch_forecasting(log_returns, historical_data['Close'].iloc[-1], time_horizon)
        print(f"ARIMA-GARCH forecast based on {size} days of historical data: ${arima_garch_forecast:.2f}")

        # Fetch actual value after 30 days for comparison
        future_date = (pd.to_datetime(end_date) + pd.Timedelta(days=time_horizon)).strftime('%Y-%m-%d')
        future_data = fetch_data(ticker_symbol, end_date, future_date)
        
        if len(future_data) > 0:
            actual_price_30d = future_data['Close'].iloc[-1]
            # Calculate percentage error for each model
            mc_error = np.abs((mc_forecast - actual_price_30d) / actual_price_30d) * 100
            arima_garch_error = np.abs((arima_garch_forecast - actual_price_30d) / actual_price_30d) * 100

            # Calculate direction accuracy for each model
            mc_direction = "up" if mc_forecast > historical_data['Close'].iloc[-1] else "down"
            arima_garch_direction = "up" if arima_garch_forecast > historical_data['Close'].iloc[-1] else "down"
            actual_direction = "up" if actual_price_30d > historical_data['Close'].iloc[-1] else "down"
            
            mc_accuracy = (mc_direction == actual_direction)
            arima_garch_accuracy = (arima_garch_direction == actual_direction)

            print(f"Actual price after {time_horizon} days: ${actual_price_30d:.2f}")
            print(f"Monte Carlo Accuracy: {'Correct' if mc_accuracy else 'Incorrect'}, Error: {mc_error:.2f}%")
            print(f"ARIMA-GARCH Accuracy: {'Correct' if arima_garch_accuracy else 'Incorrect'}, Error: {arima_garch_error:.2f}%")
        else:
            print(f"No future data available to compare for {size} days of historical data.")
        print("-" * 50)

# Example call to the backtesting function
backtest_forecasting("LDOS", historical_sizes=[365, 730], end_date="2024-04-09", time_horizon=30)
