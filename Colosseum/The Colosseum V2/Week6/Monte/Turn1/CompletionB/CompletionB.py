import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing
import datetime
from tqdm import tqdm  # For progress bar

# Original functionality - can be used standalone
def run_forecast(asset_symbol, start_date, end_date, forecast_horizon=38, visualize=True):
    # Fetch past data
    past_data = yf.download(asset_symbol, start=start_date, end=end_date)
    
    # Compute daily log returns
    daily_log_returns = np.log(past_data['Close'] / past_data['Close'].shift(1))
    daily_log_returns.dropna(inplace=True)
    daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')
    
    # Setup Monte Carlo simulation parameters
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
        norm_returns = np.random.normal(
            daily_log_returns.mean() - (curr_volatility ** 2) / 2, 
            curr_volatility / np.sqrt(252),
            simulations
        )
    
        # Update simulated prices
        simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)
    
    # Visualization of simulation
    if visualize:
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
    
    # Computing VaR and ES for Monte Carlo
    confidence_interval_mc = 0.95
    sorted_prices_mc = np.sort(simulated_prices[-1])
    VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_interval_mc) * 100)
    ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()
    
    # ARIMA model for Returns Prediction
    try:
        arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
        arima_result = arima_model.fit()
        arima_prediction = arima_result.forecast(steps=forecast_horizon)
    except:
        # Fallback to simpler model if ARIMA fails
        arima_model = ARIMA(daily_log_returns, order=(1, 0, 0))
        arima_result = arima_model.fit()
        arima_prediction = arima_result.forecast(steps=forecast_horizon)
    
    # GARCH for Volatility Prediction
    try:
        garch_model = arch_model(daily_log_returns*100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(update_freq=5, disp='off')
        garch_prediction = garch_result.forecast(horizon=forecast_horizon)
        predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100
    except:
        # Fallback to simple volatility if GARCH fails
        predicted_volatility = np.array([daily_log_returns.std()] * forecast_horizon)
    
    # Combining ARIMA and GARCH forecasts for a unified prediction
    predicted_log_return = arima_prediction.sum()
    predicted_price_arima_garch = starting_price * np.exp(predicted_log_return)
    
    # Calculating Value at Risk (VaR) and Expected Shortfall (ES) for ARIMA-GARCH
    confidence_interval = 0.95
    z_value = norm.ppf(confidence_interval)
    
    VaR_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1]))
    ES_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1] / (1 - confidence_interval)))
    
    if visualize:
        print(f"The predicted price of {asset_symbol} {forecast_horizon} days ahead is around: ${predicted_price_mc:.2f}")
        print(f"Monte Carlo Value at Risk (95% confidence): ${VaR_mc:.2f}")
        print(f"Monte Carlo Expected Shortfall: ${ES_mc:.2f}")
        print(f"Predicted price using ARIMA-GARCH: ${predicted_price_arima_garch:.2f}")
        print(f"Value at Risk using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")
        print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")
    
    return {
        'predicted_price_mc': predicted_price_mc,
        'predicted_price_arima_garch': predicted_price_arima_garch,
        'starting_price': starting_price,
        'VaR_mc': VaR_mc,
        'ES_mc': ES_mc,
        'VaR_arima_garch': VaR_arima_garch,
        'ES_arima_garch': ES_arima_garch
    }

# Backtesting function
def backtest_forecast(asset_symbol, test_windows=None, forecast_horizon=30):
    """
    Backtest the predictive efficiency of Monte Carlo and ARIMA-GARCH models.
    
    Parameters:
    - asset_symbol: Ticker symbol of the asset
    - test_windows: List of dictionaries with 'train_start', 'train_end', and 'test_date'
                   If None, creates default windows
    - forecast_horizon: Number of days to forecast ahead
    
    Returns:
    - DataFrame with backtest results
    """
    # Default backtest windows if none provided
    if test_windows is None:
        # Create test windows from 2021-01-01 to 2023-12-31, in 3-month intervals
        test_windows = []
        
        # Define the date range for backtesting
        start_date = pd.Timestamp("2021-01-01")
        end_date = pd.Timestamp("2023-10-01")  # Leaving room for forecast horizon
        
        # Create windows with different historical data lengths (180, 365, 730 days)
        historical_spans = [180, 365, 730]  # 6 months, 1 year, 2 years
        
        current_date = start_date
        while current_date <= end_date:
            for span in historical_spans:
                # Calculate training start date based on historical span
                train_start = (current_date - pd.Timedelta(days=span)).strftime('%Y-%m-%d')
                train_end = current_date.strftime('%Y-%m-%d')
                test_date = (current_date + pd.Timedelta(days=forecast_horizon)).strftime('%Y-%m-%d')
                
                test_windows.append({
                    'train_start': train_start,
                    'train_end': train_end,
                    'test_date': test_date,
                    'historical_span': span
                })
            
            # Move to next quarter
            current_date += pd.Timedelta(days=90)
    
    # Initialize results container
    results = []
    
    # Loop through each test window
    for window in tqdm(test_windows, desc="Backtesting Progress"):
        # Run forecast using training data
        forecast_results = run_forecast(
            asset_symbol=asset_symbol, 
            start_date=window['train_start'], 
            end_date=window['train_end'], 
            forecast_horizon=forecast_horizon,
            visualize=False
        )
        
        # Get actual price on test date
        try:
            actual_data = yf.download(asset_symbol, start=window['train_end'], end=window['test_date'])
            if len(actual_data) > 0:
                actual_price = actual_data['Close'].iloc[-1]
                
                # Calculate directional accuracy (1 if correct, 0 if incorrect)
                starting_price = forecast_results['starting_price']
                actual_direction = 1 if actual_price > starting_price else -1
                mc_direction = 1 if forecast_results['predicted_price_mc'] > starting_price else -1
                arima_garch_direction = 1 if forecast_results['predicted_price_arima_garch'] > starting_price else -1
                
                mc_direction_accuracy = 1 if mc_direction == actual_direction else 0
                arima_garch_direction_accuracy = 1 if arima_garch_direction == actual_direction else 0
                
                # Calculate percentage error
                mc_pct_error = abs((forecast_results['predicted_price_mc'] - actual_price) / actual_price) * 100
                arima_garch_pct_error = abs((forecast_results['predicted_price_arima_garch'] - actual_price) / actual_price) * 100
                
                # Store results
                result = {
                    'train_start': window['train_start'],
                    'train_end': window['train_end'],
                    'test_date': window['test_date'],
                    'historical_span': window.get('historical_span', None),
                    'starting_price': starting_price,
                    'actual_price': actual_price,
                    'mc_predicted_price': forecast_results['predicted_price_mc'],
                    'arima_garch_predicted_price': forecast_results['predicted_price_arima_garch'],
                    'mc_direction_accuracy': mc_direction_accuracy,
                    'arima_garch_direction_accuracy': arima_garch_direction_accuracy,
                    'mc_pct_error': mc_pct_error,
                    'arima_garch_pct_error': arima_garch_pct_error
                }
                
                results.append(result)
            else:
                print(f"Warning: No data available for testing period ending {window['test_date']}")
        except Exception as e:
            print(f"Error processing window {window}: {str(e)}")
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate summary statistics
    if len(results_df) > 0:
        summary = {
            'mc_avg_direction_accuracy': results_df['mc_direction_accuracy'].mean() * 100,
            'arima_garch_avg_direction_accuracy': results_df['arima_garch_direction_accuracy'].mean() * 100,
            'mc_avg_pct_error': results_df['mc_pct_error'].mean(),
            'arima_garch_avg_pct_error': results_df['arima_garch_pct_error'].mean()
        }
        
        print("\nBacktesting Summary:")
        print(f"Number of test windows: {len(results_df)}")
        print(f"Monte Carlo direction accuracy: {summary['mc_avg_direction_accuracy']:.2f}%")
        print(f"ARIMA-GARCH direction accuracy: {summary['arima_garch_avg_direction_accuracy']:.2f}%")
        print(f"Monte Carlo average percentage error: {summary['mc_avg_pct_error']:.2f}%")
        print(f"ARIMA-GARCH average percentage error: {summary['arima_garch_avg_pct_error']:.2f}%")
        
        # Find best historical span for each method
        if 'historical_span' in results_df.columns:
            span_performance = results_df.groupby('historical_span').agg({
                'mc_pct_error': 'mean',
                'arima_garch_pct_error': 'mean',
                'mc_direction_accuracy': 'mean',
                'arima_garch_direction_accuracy': 'mean'
            })
            
            best_span_mc_error = span_performance['mc_pct_error'].idxmin()
            best_span_arima_error = span_performance['arima_garch_pct_error'].idxmin()
            best_span_mc_direction = span_performance['mc_direction_accuracy'].idxmax()
            best_span_arima_direction = span_performance['arima_garch_direction_accuracy'].idxmax()
            
            print(f"\nBest historical span for Monte Carlo (lowest error): {best_span_mc_error} days")
            print(f"Best historical span for ARIMA-GARCH (lowest error): {best_span_arima_error} days")
            print(f"Best historical span for Monte Carlo (direction accuracy): {best_span_mc_direction} days")
            print(f"Best historical span for ARIMA-GARCH (direction accuracy): {best_span_arima_direction} days")
            
            # Visualization of performance by historical span
            plt.figure(figsize=(12, 8))
            
            # Plot percentage error by span
            plt.subplot(2, 1, 1)
            span_performance[['mc_pct_error', 'arima_garch_pct_error']].plot(kind='bar', ax=plt.gca())
            plt.title('Average Percentage Error by Historical Data Span')
            plt.ylabel('Percentage Error (%)')
            plt.xlabel('Historical Span (days)')
            plt.xticks(rotation=0)
            plt.legend(['Monte Carlo', 'ARIMA-GARCH'])
            
            # Plot direction accuracy by span
            plt.subplot(2, 1, 2)
            (span_performance[['mc_direction_accuracy', 'arima_garch_direction_accuracy']] * 100).plot(kind='bar', ax=plt.gca())
            plt.title('Direction Accuracy by Historical Data Span')
            plt.ylabel('Accuracy (%)')
            plt.xlabel('Historical Span (days)')
            plt.xticks(rotation=0)
            plt.legend(['Monte Carlo', 'ARIMA-GARCH'])
            
            plt.tight_layout()
            plt.show()
    
    return results_df

# Run the original script
if __name__ == "__main__":
    # Original script functionality
    asset_symbol = "GOOGL"
    forecast_results = run_forecast(
        asset
