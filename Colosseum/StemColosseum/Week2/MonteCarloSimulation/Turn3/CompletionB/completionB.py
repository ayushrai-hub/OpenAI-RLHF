import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Ticker symbol and initial parameters
ticker_symbol = "LDOS"

# List of historical data sizes to test (in days)
historical_sizes = [90, 180, 365, 730]  # Example: 3 months, 6 months, 1 year, 2 years

# Forecasting horizon (in days)
forecast_horizon = 30

# Store results
results = []

for size in historical_sizes:
    print(f"\nBacktesting with {size} days of historical data:")

    # Define end date (ensure actual future prices are available)
    end_date = pd.Timestamp('2024-04-09')  # Adjust as needed
    start_date = end_date - pd.Timedelta(days=size)

    # Fetch historical data for the specified period
    historical_data = yf.download(ticker_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    if len(historical_data) == 0:
        print("No historical data available for this period.")
        continue

    # Calculate daily log returns
    log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
    log_returns.dropna(inplace=True)
    log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')

    # Monte Carlo simulation parameters
    time_horizon = forecast_horizon  # Days
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
    arima_model = ARIMA(log_returns, order=(10, 0, 1))  # Adjust parameters as needed
    arima_result = arima_model.fit()
    arima_forecast = arima_result.forecast(steps=forecast_horizon)  # Forecasting next forecast_horizon days

    # GARCH for Volatility Estimation
    garch_model = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1)  # Scaling
    garch_result = garch_model.fit(update_freq=5, disp='off')
    garch_forecast = garch_result.forecast(horizon=forecast_horizon)
    forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100  # Rescaling

    # Combining ARIMA and GARCH forecasts for a standalone forecast
    forecasted_log_return = arima_forecast.sum()
    forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)
    print(f"Forecasted price using ARIMA-GARCH: ${forecasted_price_arima_garch:.2f}")

    # VaR and ES calculations for ARIMA-GARCH
    confidence_level = 0.95
    z_score = norm.ppf(confidence_level)

    VaR_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1]))
    ES_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1] / (1 - confidence_level)))
    print(f"Value at Risk using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")
    print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")

    # Fetch actual price after forecast_horizon days for comparison
    actual_end_date = end_date + pd.Timedelta(days=forecast_horizon)
    actual_data = yf.download(ticker_symbol, start=end_date.strftime('%Y-%m-%d'), end=actual_end_date.strftime('%Y-%m-%d'))

    if len(actual_data) == 0:
        print("No actual data available for the forecast horizon.")
        continue

    actual_price = actual_data['Close'].iloc[-1]
    print(f"Actual price after {forecast_horizon} days: ${actual_price:.2f}")

    # Calculate direction accuracy and percentage error for Monte Carlo forecast
    mc_direction_correct = ((forecasted_price_mc - initial_price) * (actual_price - initial_price)) > 0
    mc_percentage_error = abs(forecasted_price_mc - actual_price) / actual_price * 100

    print(f"Monte Carlo forecast direction correct: {mc_direction_correct}")
    print(f"Monte Carlo forecast percentage error: {mc_percentage_error:.2f}%")

    # Calculate direction accuracy and percentage error for ARIMA-GARCH forecast
    arima_garch_direction_correct = ((forecasted_price_arima_garch - initial_price) * (actual_price - initial_price)) > 0
    arima_garch_percentage_error = abs(forecasted_price_arima_garch - actual_price) / actual_price * 100

    print(f"ARIMA-GARCH forecast direction correct: {arima_garch_direction_correct}")
    print(f"ARIMA-GARCH forecast percentage error: {arima_garch_percentage_error:.2f}%")

    # Record results
    results.append({
        'historical_size': size,
        'forecasted_price_mc': forecasted_price_mc,
        'forecasted_price_arima_garch': forecasted_price_arima_garch,
        'actual_price': actual_price,
        'mc_direction_correct': mc_direction_correct,
        'mc_percentage_error': mc_percentage_error,
        'arima_garch_direction_correct': arima_garch_direction_correct,
        'arima_garch_percentage_error': arima_garch_percentage_error
    })

# After backtesting, analyze the results
results_df = pd.DataFrame(results)
print("\nBacktesting Results:")
print(results_df)
