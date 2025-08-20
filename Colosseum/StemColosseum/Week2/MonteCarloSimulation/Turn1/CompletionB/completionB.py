import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from datetime import timedelta

def backtest_forecasting(ticker_symbol, end_date, historical_sizes, forecast_horizon=30):
    results = []

    for size in historical_sizes:
        print(f"\nStarting backtest with {size} days of historical data.")
        
        # Adjust start date based on the historical size
        adjusted_start_date = pd.to_datetime(end_date) - pd.Timedelta(days=size)
        
        # Fetch historical data for the period
        historical_data = yf.download(ticker_symbol, start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date)
        
        if historical_data.empty:
            print(f"No data fetched for {size} days historical size. Skipping...")
            continue
        
        # Calculate daily log returns
        log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
        log_returns.dropna(inplace=True)
        log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')

        if log_returns.empty or len(log_returns) < 10:
            print(f"Insufficient log returns data for model training with {size} days. Skipping...")
            continue

        # Monte Carlo simulation
        initial_price = historical_data['Close'].iloc[-1]
        time_horizon = forecast_horizon  # Days
        num_simulations = 10000

        np.random.seed(42)
        price_paths = np.zeros((time_horizon, num_simulations))
        price_paths[0] = initial_price

        # Implementing Stochastic Volatility adjustments
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

        # ARIMA for Returns Prediction
        arima_model = ARIMA(log_returns, order=(10, 0, 1))
        arima_result = arima_model.fit()
        arima_forecast = arima_result.forecast(steps=forecast_horizon)

        # GARCH for Volatility Estimation
        garch_model = arch_model(log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(update_freq=5, disp='off')
        garch_forecast = garch_result.forecast(horizon=forecast_horizon)
        forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100

        forecasted_log_return = arima_forecast.sum()
        forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)

        # Fetch actual price after forecast horizon
        future_end_date = pd.to_datetime(end_date) + timedelta(days=forecast_horizon)
        future_data = yf.download(ticker_symbol, start=end_date, end=future_end_date.strftime('%Y-%m-%d'))

        if future_data.empty:
            print(f"No future data available from {end_date} to {future_end_date.strftime('%Y-%m-%d')}. Skipping...")
            continue

        actual_price = future_data['Close'].iloc[-1]

        # Evaluate forecasted direction and percentage error for Monte Carlo
        mc_direction_correct = ((forecasted_price_mc > initial_price) and (actual_price > initial_price)) or ((forecasted_price_mc < initial_price) and (actual_price < initial_price))
        mc_percentage_error = np.abs((forecasted_price_mc - actual_price) / actual_price) * 100

        # Evaluate forecasted direction and percentage error for ARIMA-GARCH
        ag_direction_correct = ((forecasted_price_arima_garch > initial_price) and (actual_price > initial_price)) or ((forecasted_price_arima_garch < initial_price) and (actual_price < initial_price))
        ag_percentage_error = np.abs((forecasted_price_arima_garch - actual_price) / actual_price) * 100

        results.append({
            'historical_size': size,
            'mc_forecasted_price': forecasted_price_mc,
            'arima_garch_forecasted_price': forecasted_price_arima_garch,
            'actual_price': actual_price,
            'mc_direction_correct': mc_direction_correct,
            'mc_percentage_error': mc_percentage_error,
            'ag_direction_correct': ag_direction_correct,
            'ag_percentage_error': ag_percentage_error
        })

        print(f"Monte Carlo - Forecasted Price: ${forecasted_price_mc:.2f}, Actual Price: ${actual_price:.2f}, "
              f"Direction Correct: {mc_direction_correct}, Percentage Error: {mc_percentage_error:.2f}%")
        print(f"ARIMA-GARCH - Forecasted Price: ${forecasted_price_arima_garch:.2f}, Actual Price: ${actual_price:.2f}, "
              f"Direction Correct: {ag_direction_correct}, Percentage Error: {ag_percentage_error:.2f}%")

    return pd.DataFrame(results)

# Fetch historical data
ticker_symbol = "LDOS"
historical_data = yf.download(ticker_symbol, start="2023-04-01", end="2024-04-09")

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
arima_forecast = arima_result.forecast(steps=38)  # Forecasting next 38 days

# GARCH for Volatility Estimation
garch_model = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1)  # Multiplying by 100 for scaling
garch_result = garch_model.fit(update_freq=5, disp='off')
garch_forecast = garch_result.forecast(horizon=38)
forecasted_volatility = np.sqrt(garch_forecast.variance)
