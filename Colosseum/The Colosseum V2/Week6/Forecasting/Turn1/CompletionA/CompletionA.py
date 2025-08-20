import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing
from datetime import timedelta

# Original code remains unchanged until the end
# ... [Your original code here] ...

# Add backtesting functionality
def backtest_predictions(asset_symbol, start_date, end_date, forecast_horizon=40, 
                       window_sizes=[252, 504, 756]):  # 1, 2, 3 years of trading days
    # Fetch full dataset
    full_data = yf.download(asset_symbol, start=start_date, end=end_date)
    actual_prices = full_data['Close']
    
    # Store results
    results = {
        'MonteCarlo': {'direction_accuracy': [], 'percent_error': [], 'window_sizes': window_sizes},
        'ARIMA_GARCH': {'direction_accuracy': [], 'percent_error': [], 'window_sizes': window_sizes}
    }
    
    # Calculate daily log returns for full dataset
    full_log_returns = np.log(full_data['Close'] / full_data['Close'].shift(1))
    full_log_returns.dropna(inplace=True)
    full_log_returns.index = pd.DatetimeIndex(full_log_returns.index).to_period('D')
    
    for window in window_sizes:
        # Ensure we have enough data for prediction + actual comparison
        n_iterations = len(actual_prices) - window - forecast_horizon
        
        if n_iterations <= 0:
            print(f"Skipping window {window} - insufficient data")
            continue
            
        mc_directions = []
        mc_errors = []
        ag_directions = []
        ag_errors = []
        
        for i in range(n_iterations):
            # Define training period
            train_start = i
            train_end = i + window
            
            # Get training data
            past_data = actual_prices.iloc[train_start:train_end]
            train_returns = full_log_returns.iloc[train_start:train_end]
            
            # Actual future price
            actual_future_price = actual_prices.iloc[train_end + forecast_horizon - 1]
            
            # Monte Carlo Simulation
            starting_price = past_data.iloc[-1]
            curr_volatility = train_returns.std()
            vol_shock_intensity = 0.35
            peak_volatility = curr_volatility * 2
            
            simulated_prices = np.zeros((forecast_horizon, simulations))
            simulated_prices[0] = starting_price
            
            np.random.seed(24)
            for t in range(1, forecast_horizon):
                vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
                curr_volatility = np.abs(curr_volatility + vol_shock)
                curr_volatility = np.minimum(curr_volatility, peak_volatility)
                norm_returns = np.random.normal(train_returns.mean() - (curr_volatility ** 2) / 2, 
                                             curr_volatility / np.sqrt(252), simulations)
                simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)
            
            mc_predicted = simulated_prices[-1].mean()
            
            # ARIMA-GARCH
            try:
                arima_model = ARIMA(train_returns, order=(5, 0, 2))
                arima_result = arima_model.fit()
                arima_pred = arima_result.forecast(steps=forecast_horizon)
                
                garch_model = arch_model(train_returns*100, mean='Zero', vol='Garch', p=1, q=1)
                garch_result = garch_model.fit(update_freq=5, disp='off')
                garch_pred = garch_result.forecast(horizon=forecast_horizon)
                
                ag_predicted = starting_price * np.exp(arima_pred.sum() / 100)
                
                # Evaluate predictions
                # Direction accuracy
                mc_direction = 1 if mc_predicted > starting_price else 0
                ag_direction = 1 if ag_predicted > starting_price else 0
                actual_direction = 1 if actual_future_price > starting_price else 0
                
                mc_directions.append(mc_direction == actual_direction)
                ag_directions.append(ag_direction == actual_direction)
                
                # Percent error
                mc_error = abs(mc_predicted - actual_future_price) / actual_future_price * 100
                ag_error = abs(ag_predicted - actual_future_price) / actual_future_price * 100
                mc_errors.append(mc_error)
                ag_errors.append(ag_error)
            
            except Exception as e:
                print(f"Error in iteration {i} for window {window}: {str(e)}")
                continue
        
        # Store results for this window
        results['MonteCarlo']['direction_accuracy'].append(np.mean(mc_directions))
        results['MonteCarlo']['percent_error'].append(np.mean(mc_errors))
        results['ARIMA_GARCH']['direction_accuracy'].append(np.mean(ag_directions))
        results['ARIMA_GARCH']['percent_error'].append(np.mean(ag_errors))
    
    # Print results
    print("\nBacktesting Results:")
    for model in results:
        print(f"\n{model}:")
        for i, window in enumerate(results[model]['window_sizes']):
            if i < len(results[model]['direction_accuracy']):
                print(f"Window {window} days:")
                print(f"  Direction Accuracy: {results[model]['direction_accuracy'][i]:.2%}")
                print(f"  Average Percent Error: {results[model]['percent_error'][i]:.2f}%")
    
    # Plot results
    plt.figure(figsize=(12, 6))
    for model in results:
        plt.plot(results[model]['window_sizes'], results[model]['direction_accuracy'], 
                marker='o', label=f"{model} Direction Accuracy")
        plt.plot(results[model]['window_sizes'], 
                [x/100 for x in results[model]['percent_error']], 
                marker='x', label=f"{model} Percent Error (scaled)")
    plt.xlabel("Window Size (days)")
    plt.ylabel("Metric Value")
    plt.title("Backtesting Results Across Different Window Sizes")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return results

# Run original analysis
# ... [Your original code here] ...

# Run backtesting
print("\nStarting backtesting...")
backtest_results = backtest_predictions(
    asset_symbol="GOOGL",
    start_date="2020-01-01",
    end_date="2025-02-21",
    forecast_horizon=40
)
