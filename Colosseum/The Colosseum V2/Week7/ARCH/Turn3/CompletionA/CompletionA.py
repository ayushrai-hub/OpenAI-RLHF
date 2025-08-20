import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Fetch past data
asset_symbol = "GOOGL"
past_data = yf.download(asset_symbol, start="2023-01-01", end="2024-01-30")

# Compute daily log returns
daily_log_returns = np.log(past_data['Close'] / past_data['Close'].shift(1))
daily_log_returns.dropna(inplace=True)
daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')

# Setup Monte Carlo simulation parameters
forecast_horizon = 40  # Days
simulations = 10000
starting_price = past_data['Close'].iloc[-1]

# Initiate simulation
np.random.seed(24)
simulated_prices = np.zeros((forecast_horizon, simulations))
simulated_prices[0] = starting_price

# Perform Stochastic Volatility with a checked volatility shock threshold
curr_volatility = daily_log_returns.std()
vol_shock_intensity = 0.35  # Volatility of volatility
peak_volatility = curr_volatility * 2  # Max limit to control explosion

for t in range(1, forecast_horizon):
    # Random shock for volatility capped
    vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
    curr_volatility = np.abs(curr_volatility + vol_shock)
    curr_volatility = np.minimum(curr_volatility, peak_volatility)

    # Geometric Brownian Motion with adjusted volatility
    norm_returns = np.random.normal(daily_log_returns.mean() - (curr_volatility ** 2) / 2, curr_volatility / np.sqrt(252),
                                    simulations)

    # Update simulated prices
    simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)

# Visualization of simulation
plt.figure(figsize=(10, 6))
for i in range(simulations):
    plt.plot(simulated_prices[:, i], linewidth=0.5, alpha=0.2, color='gray')
plt.plot(simulated_prices.mean(axis=1), color='blue', linewidth=2, label='Average Path')
plt.title(f"Monte Carlo Simulation of {asset_symbol} Over {forecast_horizon} Days")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show()

# Estimating the price using Monte Carlo
predicted_price_mc = simulated_prices[-1].mean()
print(f"The predicted price of {asset_symbol} {forecast_horizon} days ahead is around: ${predicted_price_mc:.2f}")

# Computing VaR and ES for Monte Carlo
confidence_interval_mc = 0.95
sorted_prices_mc = np.sort(simulated_prices[-1])
VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_interval_mc) * 100)
ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()

print(f"Monte Carlo Value at Risk (95% confidence): ${VaR_mc:.2f}")
print(f"Monte Carlo Expected Shortfall: ${ES_mc:.2f}")

# ARIMA model for Returns Prediction
arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
arima_result = arima_model.fit()
arima_prediction = arima_result.forecast(steps=38)  # Predicting next 38 days

# GARCH for Volatility Prediction
garch_model = arch_model(daily_log_returns*100, mean='Zero', vol='Garch', p=1, q=1)
garch_result = garch_model.fit(update_freq=5, disp='off')
garch_prediction = garch_result.forecast(horizon=38)
predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100

# Combining ARIMA and GARCH forecasts
predicted_log_return = arima_prediction.sum()  # No additional scaling
predicted_price_arima_garch = starting_price * np.exp(predicted_log_return)
print(f"Predicted price using ARIMA-GARCH: ${predicted_price_arima_garch:.2f}")

# Calculating Value at Risk (VaR) and Expected Shortfall (ES) for ARIMA-GARCH
confidence_interval = 0.95
z_value = norm.ppf(confidence_interval)

VaR_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1]))
ES_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1] / (1 - confidence_interval)))
print(f"Value at Risk using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")
print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")


