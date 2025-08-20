import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Fetch historical data
start_date = "2023-04-01"
end_date = "2024-04-09"
ticker_symbol = "LDOS"

# Function to fetch historical data
def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

#historical_data = yf.download(ticker_symbol, start=start_date, end=end_date)
historical_data = fetch_data(ticker_symbol, start_date, end_date)

# Calculate daily log returns
log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
log_returns.dropna(inplace=True)
log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')

# Monte Carlo simulation parameters
time_horizon = 38  # Days
num_simulations = 10000
initial_price = historical_data['Close'].iloc[-1]

# Prepare for simulation
np.random.seed(42)
price_paths = np.zeros((time_horizon, num_simulations))
price_paths[0] = initial_price

# Implementing Stochastic Volatility adjustments with a realistic volatility shock cap
volatility = log_returns.std()
vol_volatility = 0.4  # Volatility of volatility
max_volatility = volatility * 2  # Cap to prevent explosion

for t in range(1, time_horizon):
    # Random shock for volatility with cap
    vol_shock = np.random.normal(0, vol_volatility, num_simulations)
    volatility = np.abs(volatility + vol_shock)
    volatility = np.minimum(volatility, max_volatility)

    # GBM component with adjusted volatility
    normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2, volatility / np.sqrt(252),
                                      num_simulations)

    # Update price paths
    price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)

# Plotting the simulation
plt.figure(figsize=(10, 6))
for i in range(num_simulations):
    plt.plot(price_paths[:, i], linewidth=0.5, alpha=0.2, color='gray')
plt.plot(price_paths.mean(axis=1), color='red', linewidth=2, label='Average Path')
plt.title(f"Monte Carlo Simulation of {ticker_symbol} Over {time_horizon} Days")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show()

# Forecasting the price using Monte Carlo
forecasted_price_mc = price_paths[-1].mean()
print(f"The forecasted price of {ticker_symbol} {time_horizon} days out is approximately: ${forecasted_price_mc:.2f}")

# VaR and ES for Monte Carlo
confidence_level_mc = 0.95
sorted_prices_mc = np.sort(price_paths[-1])
VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_level_mc) * 100)
ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()

print(f"Monte Carlo Value at Risk (95% confidence): ${VaR_mc:.2f}")
print(f"Monte Carlo Expected Shortfall: ${ES_mc:.2f}")

# ARIMA for Returns Prediction
arima_model = ARIMA(log_returns, order=(10, 0, 1))  # Example parameters; adjust based on your dataset
arima_result = arima_model.fit()
arima_forecast = arima_result.forecast(steps=38)  # Forecasting next 30 days

# GARCH for Volatility Estimation
garch_model = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1)  # Multiplying by 100 for scaling
garch_result = garch_model.fit(update_freq=5, disp='off')
garch_forecast = garch_result.forecast(horizon=38)
forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100  # Dividing by 100 to rescale

# Combining ARIMA and GARCH forecasts for a standalone forecast
forecasted_log_return = arima_forecast.sum()
forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)
print(f"Forecasted price using ARIMA-GARCH: ${forecasted_price_arima_garch:.2f}")

# Value at Risk (VaR) and Expected Shortfall (ES) calculations for ARIMA-GARCH
confidence_level = 0.95
z_score = norm.ppf(confidence_level)

VaR_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1]))
ES_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1] / (1 - confidence_level)))
print(f"Value at Risk using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")
print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")



# Function to calculate log returns
def calculate_log_returns(data):
    log_returns = np.log(data / data.shift(1))
    log_returns.dropna(inplace=True)
    return log_returns

# Main function for backtesting
def backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes):
    results = {}
    for size in historical_sizes:
        adjusted_start_date = pd.to_datetime(end_date) - pd.Timedelta(days=size)
        historical_data = fetch_data(ticker_symbol, adjusted_start_date.strftime('%Y-%m-%d'), end_date)['Close']
        log_returns = calculate_log_returns(historical_data)

        # Set up for Monte Carlo simulation
        time_horizon = 38
        num_simulations = 10000
        initial_price = historical_data.iloc[-1]
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
            normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2, volatility / np.sqrt(252), num_simulations)
            price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)

        forecasted_price_mc = price_paths[-1].mean()

        # ARIMA and GARCH models
        arima_model = ARIMA(log_returns, order=(10, 0, 1))
        arima_result = arima_model.fit()
        arima_forecast = arima_result.forecast(steps=38)
        garch_model = arch_model(log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(disp='off')
        garch_forecast = garch_result.forecast(horizon=38)
        forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100
        forecasted_log_return = arima_forecast.sum()
        forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)

        # Fetch actual price after 30 days for comparison
        future_end_date = pd.to_datetime(end_date) + pd.Timedelta(days=30)
        future_data = fetch_data(ticker_symbol, end_date, future_end_date.strftime('%Y-%m-%d'))['Close']
        actual_price_30d = future_data.iloc[-1]

        # Calculate accuracy metrics
        direction_accuracy_mc = (np.sign(forecasted_price_mc - initial_price) == np.sign(actual_price_30d - initial_price))
        percentage_error_mc = np.abs((forecasted_price_mc - actual_price_30d) / actual_price_30d) * 100
        direction_accuracy_arima_garch = (np.sign(forecasted_price_arima_garch - initial_price) == np.sign(actual_price_30d - initial_price))
        percentage_error_arima_garch = np.abs((forecasted_price_arima_garch - actual_price_30d) / actual_price_30d) * 100

        results[size] = {
            "MC Direction Accuracy": direction_accuracy_mc,
            "MC Percentage Error": percentage_error_mc,
            "ARIMA-GARCH Direction Accuracy": direction_accuracy_arima_garch,
            "ARIMA-GARCH Percentage Error": percentage_error_arima_garch
        }

    return results

# Example call to the backtesting function
historical_sizes = [365, 730]  # Testing with 1 and 2 years of historical data
results = backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes)
print(results)
