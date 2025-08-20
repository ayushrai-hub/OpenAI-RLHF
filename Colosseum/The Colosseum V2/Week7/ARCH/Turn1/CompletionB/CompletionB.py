import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# --- Original code starts here ---

def run_forecast(asset_symbol, start_date, end_date, forecast_horizon=38, simulations=10000):
    """
    Runs Monte Carlo and ARIMA-GARCH forecasts for a specified asset
    over a given historical period.

    Returns:
        (dict): containing forecasts and intermediate results.
    """
    # Fetch past data
    past_data = yf.download(asset_symbol, start=start_date, end=end_date)

    # Compute daily log returns
    daily_log_returns = np.log(past_data['Close'] / past_data['Close'].shift(1))
    daily_log_returns.dropna(inplace=True)
    daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')

    # Setup Monte Carlo simulation parameters
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
        simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)

    # Estimating the price using Monte Carlo
    predicted_price_mc = simulated_prices[-1].mean()

    # Computing VaR and ES for Monte Carlo
    confidence_interval_mc = 0.95
    sorted_prices_mc = np.sort(simulated_prices[-1])
    VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_interval_mc) * 100)
    ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()

    # ARIMA model for Returns Prediction
    arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))  # Example parameters
    arima_result = arima_model.fit()
    arima_prediction = arima_result.forecast(steps=forecast_horizon)

    # GARCH for Volatility Prediction
    garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)  
    garch_result = garch_model.fit(update_freq=5, disp='off')
    garch_prediction = garch_result.forecast(horizon=forecast_horizon)
    predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100

    # Combining ARIMA and GARCH forecasts for a unified prediction
    predicted_log_return = arima_prediction.sum()
    predicted_price_arima_garch = starting_price * np.exp(predicted_log_return / 100)

    # Calculating VaR and ES for ARIMA-GARCH
    confidence_interval = 0.95
    z_value = norm.ppf(confidence_interval)
    VaR_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1]))
    ES_arima_garch = (starting_price -
                      (starting_price * np.exp(-z_value * predicted_volatility[-1] /
                                               (1 - confidence_interval))))

    return {
        'past_data': past_data,
        'daily_log_returns': daily_log_returns,
        'simulated_prices': simulated_prices,
        'predicted_price_mc': predicted_price_mc,
        'VaR_mc': VaR_mc,
        'ES_mc': ES_mc,
        'predicted_price_arima_garch': predicted_price_arima_garch,
        'VaR_arima_garch': VaR_arima_garch,
        'ES_arima_garch': ES_arima_garch
    }

def plot_simulation(simulated_prices, forecast_horizon, asset_symbol):
    """Plot Monte Carlo simulation results."""
    plt.figure(figsize=(10, 6))
    for i in range(simulated_prices.shape[1]):
        plt.plot(simulated_prices[:, i], linewidth=0.5, alpha=0.2, color='gray')
    plt.plot(simulated_prices.mean(axis=1), color='blue', linewidth=2, label='Average Path')
    plt.title(f"Monte Carlo Simulation of {asset_symbol} Over {forecast_horizon} Days")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend()
    plt.show()

# --- Backtesting functionality below ---

def backtest_forecast(asset_symbol, historical_spans, end_date="2024-01-30", forecast_horizon=38):
    """
    Backtest the predictive efficiency of both the Monte Carlo simulation
    and ARIMA-GARCH by iterating over multiple historical data spans.

    Args:
        asset_symbol (str): The ticker symbol of the asset.
        historical_spans (list of int): Each integer is # of days used as a historical window.
        end_date (str): The end date for the historical data segment.
        forecast_horizon (int): The number of days ahead to forecast.

    Returns:
        A DataFrame summarizing the direction accuracy and percentage error
        for each historical span and each method.
    """
    results = []

    # Pre-download data up to 38 days after end_date to compare actual future price
    backtest_end_dt = pd.to_datetime(end_date)
    compare_end_dt = backtest_end_dt + pd.Timedelta(days=forecast_horizon)
    full_data = yf.download(asset_symbol, start="2022-01-01", end=compare_end_dt.strftime('%Y-%m-%d'))

    for span in historical_spans:
        # Calculate new start date
        start_dt = backtest_end_dt - pd.Timedelta(days=span)
        hist_data = full_data.loc[start_dt:end_date]

        # If hist_data is insufficient, skip
        if len(hist_data) < 2:
            print(f"Insufficient data for span={span}. Skipping.")
            continue

        # Run forecast with the chosen historical data
        forecast_result = run_forecast(asset_symbol,
                                       start_date=start_dt.strftime('%Y-%m-%d'),
                                       end_date=end_date,
                                       forecast_horizon=forecast_horizon)

        # Compute actual price after forecast horizon
        comparison_data = full_data.loc[end_date:compare_end_dt]
        
        # If no future data available for comparison, skip
        if len(comparison_data) < 2:
            print(f"No future data for comparison for span={span}. Skipping.")
            continue

        actual_price_38d = comparison_data['Close'].iloc[-1]
        last_price = hist_data['Close'].iloc[-1]

        # Evaluate direction accuracy
        # (positive if the price increased, negative if it decreased)
        actual_direction = np.sign(actual_price_38d - last_price)
        mc_direction = np.sign(forecast_result['predicted_price_mc'] - last_price)
        arima_garch_direction = np.sign(forecast_result['predicted_price_arima_garch'] - last_price)

        mc_direction_accuracy = (mc_direction == actual_direction)
        arima_garch_direction_accuracy = (arima_garch_direction == actual_direction)

        # Evaluate percentage error
        mc_pct_error = 100.0 * abs(forecast_result['predicted_price_mc'] - actual_price_38d) / actual_price_38d
        arima_garch_pct_error = 100.0 * abs(forecast_result['predicted_price_arima_garch'] - actual_price_38d) / actual_price_38d

        # Append results with all necessary metrics
        results.append({
            'Historical Span (days)': span,
            'Last Historical Price': last_price,
            'Predicted MC Price': forecast_result['predicted_price_mc'],
            'Predicted ARIMA-GARCH Price': forecast_result['predicted_price_arima_garch'],
            'Actual Future Price': actual_price_38d,
            'MC Direction Accuracy': mc_direction_accuracy,
            'ARIMA-GARCH Direction Accuracy': arima_garch_direction_accuracy,
            'MC Percentage Error': mc_pct_error,
            'ARIMA-GARCH Percentage Error': arima_garch_pct_error
        })

