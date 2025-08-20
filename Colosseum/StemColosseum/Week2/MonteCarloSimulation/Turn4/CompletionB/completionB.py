import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

def fetch_data(ticker_symbol, start_date, end_date):
    """Fetch historical data for the given ticker."""
    return yf.download(ticker_symbol, start=start_date, end=end_date)

def calculate_log_returns(historical_data):
    """Calculate daily log returns from historical data."""
    log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
    log_returns.dropna(inplace=True)
    log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')
    return log_returns

def monte_carlo_simulation(log_returns, initial_price, time_horizon, num_simulations=10000):
    """Perform a Monte Carlo simulation for the price forecast."""
    # Simulation setup
    np.random.seed(42)
    price_paths = np.zeros((time_horizon, num_simulations))
    price_paths[0] = initial_price

    # Stochastic volatility with a cap
    volatility = log_returns.std()
    vol_volatility = 0.4
    max_volatility = volatility * 2

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

    return price_paths

def arima_garch_forecast(log_returns, initial_price, time_horizon):
    """Forecast price using ARIMA-GARCH model."""
    # ARIMA model
    arima_model = ARIMA(log_returns, order=(10, 0, 1))
    arima_result = arima_model.fit()
    arima_forecast = arima_result.forecast(steps=time_horizon)

    # GARCH for volatility estimation
    garch_model = arch_model(log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
    garch_result = garch_model.fit(update_freq=5, disp='off')
    garch_forecast = garch_result.forecast(horizon=time_horizon)
    forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100

    # Combining ARIMA and GARCH forecasts
    forecasted_log_return = arima_forecast.sum()
    forecasted_price = initial_price * np.exp(forecasted_log_return / 100)

    return forecasted_price, forecasted_volatility[-1]

def evaluate_forecasts(forecasted_price, actual_price):
    """Calculate direction accuracy and percentage error."""
    direction_correct = np.sign(forecasted_price - actual_price) == np.sign(actual_price - actual_price)
    percent_error = np.abs(forecasted_price - actual_price) / actual_price * 100
    return direction_correct, percent_error

def backtest_forecasting(ticker_symbol, end_date, historical_sizes, time_horizon=38):
    """Backtest forecasting models over varying historical data sizes."""
    results = []

    for size in historical_sizes:
        # Adjust start date based on size
        adjusted_start_date = pd.to_datetime(end_date) - pd.Timedelta(days=size)
        
        # Fetch historical data and log returns
        historical_data = fetch_data(ticker_symbol, adjusted_start_date, end_date)
        log_returns = calculate_log_returns(historical_data)
        
        # Monte Carlo simulation
        initial_price = historical_data['Close'].iloc[-1]
        price_paths = monte_carlo_simulation(log_returns, initial_price, time_horizon)
        forecasted_price_mc = price_paths[-1].mean()

        # ARIMA-GARCH forecast
        forecasted_price_arima_garch, forecasted_volatility = arima_garch_forecast(log_returns, initial_price, time_horizon)

        # Obtain actual price after 30 days for backtesting
        future_end_date = pd.to_datetime(end_date) + pd.Timedelta(days=30)
        future_data = fetch_data(ticker_symbol, end_date, future_end_date)
        actual_price_30d = future_data['Close'].iloc[-1]

        # Evaluate forecast accuracy for both methods
        direction_correct_mc, percent_error_mc = evaluate_forecasts(forecasted_price_mc, actual_price_30d)
        direction_correct_arima_garch, percent_error_arima_garch = evaluate_forecasts(forecasted_price_arima_garch, actual_price_30d)
        
        results.append({
            "Historical Size (days)": size,
            "Forecasted Price (Monte Carlo)": forecasted_price_mc,
            "Forecasted Price (ARIMA-GARCH)": forecasted_price_arima_garch,
            "Actual Price (30 days later)": actual_price_30d,
            "Direction Correct (Monte Carlo)": direction_correct_mc,
            "Percent Error (Monte Carlo)": percent_error_mc,
            "Direction Correct (ARIMA-GARCH)": direction_correct_arima_garch,
            "Percent Error (ARIMA-GARCH)": percent_error_arima_garch
        })

    # Display results
    results_df = pd.DataFrame(results)
    print(results_df)

    return results_df

# Example usage of backtesting
ticker_symbol = "LDOS"
historical_sizes = [180, 365, 730]  # 6 months, 1 year, 2 years
end_date = "2024-04-09"
backtest_results = backtest_forecasting(ticker_symbol, end_date, historical_sizes, time_horizon=38)

# Plot Monte Carlo Simulation Result
plt.figure(figsize=(10, 6))
for i in range(price_paths.shape[1]):
    plt.plot(price_paths[:, i], linewidth=0.5, alpha=0.2, color='gray')
plt.plot(price_paths.mean(axis=1), color='red', linewidth=2, label='Average Path')
plt.title(f"Monte Carlo Simulation of {ticker_symbol} Over {time_horizon} Days")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show()

# Monte Carlo VaR and ES
confidence_level_mc = 0.95
sorted_prices_mc = np.sort(price_paths[-1])
VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_level_mc) * 100)
ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()

print(f"Monte Carlo Value at Risk (95% confidence): ${VaR_mc:.2f}")
print(f"Monte Carlo Expected Shortfall: ${ES_mc:.2f}")

# ARIMA-GARCH VaR and ES
confidence_level = 0.95
z_score = norm.ppf(confidence_level)

VaR_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility))
ES_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility / (1 - confidence_level)))
print(f"Value at Risk using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")
print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")
