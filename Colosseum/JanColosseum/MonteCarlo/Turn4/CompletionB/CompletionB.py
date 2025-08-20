import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# Function to backtest forecasting models
def backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes, time_horizon=30):
    results = []
    
    # Fetch actual price for evaluating forecasts after time_horizon days
    future_end_date = pd.to_datetime(end_date) + pd.Timedelta(days=time_horizon)
    
    # Loop through different historical data sizes
    for size in historical_sizes:
        adjusted_start_date = pd.to_datetime(end_date) - pd.Timedelta(days=size)
        
        # Fetch and prepare historical data
        historical_data = yf.download(ticker_symbol, start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date)
        if len(historical_data) < size:  # Ensure enough data
            continue
        
        # Calculate daily log returns
        log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
        log_returns.dropna(inplace=True)
        log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')
        
        # Monte Carlo simulation parameters
        initial_price = historical_data['Close'].iloc[-1]
        num_simulations = 10000
        
        # Prepare for Monte Carlo simulation
        np.random.seed(42)
        price_paths = np.zeros((time_horizon, num_simulations))
        price_paths[0] = initial_price
        
        # Stochastic Volatility Model for Monte Carlo
        volatility = log_returns.std()
        vol_volatility = 0.4
        max_volatility = volatility * 2
        
        for t in range(1, time_horizon):
            vol_shock = np.random.normal(0, vol_volatility, num_simulations)
            volatility = np.abs(volatility + vol_shock)
            volatility = np.minimum(volatility, max_volatility)
            normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2, volatility / np.sqrt(252), num_simulations)
            price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)
        
        # Forecasted prices for Monte Carlo
        forecasted_price_mc = price_paths[-1].mean()
        
        # ARIMA-GARCH Forecast
        arima_model = ARIMA(log_returns, order=(10, 0, 1))
        arima_result = arima_model.fit()
        arima_forecast = arima_result.forecast(steps=time_horizon)
        
        garch_model = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(update_freq=5, disp='off')
        garch_forecast = garch_result.forecast(horizon=time_horizon)
        forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100
        
        forecasted_log_return = arima_forecast.sum()
        forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)
        
        # Fetch actual price after 30 days for comparison
        future_data = yf.download(ticker_symbol, start=end_date, end=future_end_date.strftime('%Y-%m-%d'))
        if not future_data.empty:
            actual_price_30d = future_data['Close'].iloc[-1]
            
            # Calculate direction accuracy
            actual_direction = np.sign(actual_price_30d - initial_price)
            monte_carlo_direction = np.sign(forecasted_price_mc - initial_price)
            arima_garch_direction = np.sign(forecasted_price_arima_garch - initial_price)
            
            mc_direction_accuracy = (monte_carlo_direction == actual_direction)
            arima_garch_direction_accuracy = (arima_garch_direction == actual_direction)
            
            # Calculate percentage error
            mc_percentage_error = np.abs((forecasted_price_mc - actual_price_30d) / actual_price_30d) * 100
            arima_garch_percentage_error = np.abs((forecasted_price_arima_garch - actual_price_30d) / actual_price_30d) * 100
            
            # Store results
            results.append({
                'historical_size': size,
                'forecasted_price_mc': forecasted_price_mc,
                'forecasted_price_arima_garch': forecasted_price_arima_garch,
                'actual_price': actual_price_30d,
                'mc_direction_accuracy': mc_direction_accuracy,
                'arima_garch_direction_accuracy': arima_garch_direction_accuracy,
                'mc_percentage_error': mc_percentage_error,
                'arima_garch_percentage_error': arima_garch_percentage_error
            })
    
    return pd.DataFrame(results)

# Set parameters for backtesting
ticker_symbol = "LDOS"
start_date = "2023-04-01"
end_date = "2024-04-09"
historical_sizes = [365, 730, 1095]  # 1 year, 2 years, 3 years

# Run backtest
backtest_results = backtest_forecasting(ticker_symbol, start_date, end_date, historical_sizes, time_horizon=30)

# Display the results of the backtest
print(backtest_results)

# Plot the results for comparison - percentage error for both methods
plt.figure(figsize=(10, 6))
plt.plot(backtest_results['historical_size'], backtest_results['mc_percentage_error'], label="MC Percentage Error")
plt.plot(backtest_results['historical_size'], backtest_results['arima_garch_percentage_error'], label="ARIMA-GARCH Percentage Error")
plt.xlabel('Historical Data Window Size (days)')
plt.ylabel('Percentage Error (%)')
plt.title('Percentage Error of Monte Carlo vs ARIMA-GARCH Forecasts')
plt.legend()
plt.show()

# Output direction accuracy as well
print(f"Monte Carlo direction accuracy: {backtest_results['mc_direction_accuracy'].mean() * 100:.2f}%")
print(f"ARIMA-GARCH direction accuracy: {backtest_results['arima_garch_direction_accuracy'].mean() * 100:.2f}%")
