import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

# -------------------------------
# Helper function: Run forecasts
# -------------------------------
def run_forecasts(historical_data, forecast_horizon=38, simulations=10000, plot_simulation=False):
    """
    Run both the Monte Carlo simulation and ARIMA-GARCH forecasting methods.
    Returns forecasted prices and risk measures.
    """
    # Compute daily log returns
    daily_log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
    daily_log_returns.dropna(inplace=True)
    daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')
    
    # Use the last close as the starting price
    starting_price = historical_data['Close'].iloc[-1]

    # -------------------------------
    # Monte Carlo Simulation
    # -------------------------------
    np.random.seed(24)
    simulated_prices = np.zeros((forecast_horizon, simulations))
    simulated_prices[0] = starting_price

    curr_volatility = daily_log_returns.std()
    vol_shock_intensity = 0.35  # volatility of volatility
    peak_volatility = curr_volatility * 2  # maximum allowed volatility

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

    # Optional: Plot simulation paths for one forecast run
    if plot_simulation:
        plt.figure(figsize=(10, 6))
        for i in range(simulations):
            plt.plot(simulated_prices[:, i], linewidth=0.5, alpha=0.2, color='gray')
        plt.plot(simulated_prices.mean(axis=1), color='blue', linewidth=2, label='Average Path')
        plt.title(f"Monte Carlo Simulation over {forecast_horizon} Days")
        plt.xlabel("Days")
        plt.ylabel("Price")
        plt.legend()
        plt.show()

    predicted_price_mc = simulated_prices[-1].mean()
    confidence_interval_mc = 0.95
    sorted_prices_mc = np.sort(simulated_prices[-1])
    VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_interval_mc) * 100)
    ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()

    # -------------------------------
    # ARIMA-GARCH Forecasting
    # -------------------------------
    # ARIMA model for returns prediction
    try:
        arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
        arima_result = arima_model.fit()
        arima_prediction = arima_result.forecast(steps=forecast_horizon)
    except Exception as e:
        print("ARIMA error:", e)
        arima_prediction = pd.Series([0]*forecast_horizon)

    # GARCH for volatility prediction
    try:
        garch_model = arch_model(daily_log_returns*100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(update_freq=5, disp='off')
        garch_prediction = garch_result.forecast(horizon=forecast_horizon)
        predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100
    except Exception as e:
        print("GARCH error:", e)
        predicted_volatility = np.array([daily_log_returns.std()]*forecast_horizon)

    # Combining forecasts: We sum the ARIMA-predicted log returns over the horizon.
    predicted_log_return = arima_prediction.sum()
    # (Note: original code scales by 100; here we keep that for consistency)
    predicted_price_arima_garch = starting_price * np.exp(predicted_log_return / 100)

    confidence_interval = 0.95
    z_value = norm.ppf(confidence_interval)
    VaR_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1]))
    ES_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1] / (1 - confidence_interval)))
    
    return {
        'starting_price': starting_price,
        'predicted_price_mc': predicted_price_mc,
        'VaR_mc': VaR_mc,
        'ES_mc': ES_mc,
        'predicted_price_arima_garch': predicted_price_arima_garch,
        'VaR_arima_garch': VaR_arima_garch,
        'ES_arima_garch': ES_arima_garch
    }

# -------------------------------
# Backtesting Function
# -------------------------------
def backtest_forecasts(asset_symbol, base_start_date, base_end_date, forecast_horizon=38, historical_spans=[365, 730]):
    """
    Backtest the forecasting methods over different historical spans.
    
    Parameters:
      - asset_symbol: string, e.g., "GOOGL"
      - base_start_date: the earliest date available (for downloading full history)
      - base_end_date: the end date for the training period in each backtest
      - forecast_horizon: number of days to forecast ahead
      - historical_spans: list of integers representing the number of days of history to use
    """
    # First, download a long-enough history for backtesting
    full_history = yf.download(asset_symbol, start=base_start_date, end=base_end_date)
    full_history.index = pd.to_datetime(full_history.index)

    for span in historical_spans:
        # Determine the training start date for this span.
        training_start_date = pd.to_datetime(base_end_date) - pd.Timedelta(days=span)
        training_data = full_history.loc[training_start_date:base_end_date]

        if training_data.empty:
            print(f"No data found for span of {span} days ending {base_end_date}.")
            continue

        # Run forecasting methods on the training data.
        forecasts = run_forecasts(training_data, forecast_horizon=forecast_horizon, simulations=10000, plot_simulation=False)
        
        # Print forecasted prices and risk metrics.
        print(f"\n=== Backtest for Historical Span = {span} days ===")
        print(f"Starting Price (as of {base_end_date}): ${forecasts['starting_price']:.2f}")
        print(f"Monte Carlo predicted price ({forecast_horizon} days ahead): ${forecasts['predicted_price_mc']:.2f}")
        print(f"   Monte Carlo VaR (95%): ${forecasts['VaR_mc']:.2f}")
        print(f"   Monte Carlo ES: ${forecasts['ES_mc']:.2f}")
        print(f"ARIMA-GARCH predicted price ({forecast_horizon} days ahead): ${forecasts['predicted_price_arima_garch']:.2f}")
        print(f"   ARIMA-GARCH VaR (95%): ${forecasts['VaR_arima_garch']:.2f}")
        print(f"   ARIMA-GARCH ES: ${forecasts['ES_arima_garch']:.2f}")

        # ---------------------------------------
        # Compare against the actual future price
        # ---------------------------------------
        # Define the future window: from base_end_date to forecast_horizon days later.
        future_start = pd.to_datetime(base_end_date)
        future_end = future_start + pd.Timedelta(days=forecast_horizon)
        
        future_data = yf.download(asset_symbol, start=future_start.strftime('%Y-%m-%d'),
                                  end=future_end.strftime('%Y-%m-%d'))
        if future_data.empty:
            print("Future data not available for comparison.")
            continue

        actual_future_price = future_data['Close'].iloc[-1]
        print(f"Actual price after {forecast_horizon} days: ${actual_future_price:.2f}")

        # Direction accuracy: Did the method predict an upward move?
        def direction_accuracy(predicted, starting, actual):
            predicted_direction = "up" if predicted > starting else "down"
            actual_direction = "up" if actual > starting else "down"
            accuracy = predicted_direction == actual_direction
            return predicted_direction, actual_direction, accuracy

        mc_dir_pred, mc_dir_actual, mc_correct = direction_accuracy(
            forecasts['predicted_price_mc'], forecasts['starting_price'], actual_future_price
        )
        arima_dir_pred, arima_dir_actual, arima_correct = direction_accuracy(
            forecasts['predicted_price_arima_garch'], forecasts['starting_price'], actual_future_price
        )

        print("\nDirection Accuracy:")
        print(f"Monte Carlo: Predicted {mc_dir_pred}, Actual {mc_dir_actual} -> {'Correct' if mc_correct else 'Incorrect'}")
        print(f"ARIMA-GARCH: Predicted {arima_dir_pred}, Actual {arima_dir_actual} -> {'Correct' if arima_correct else 'Incorrect'}")

        # Percentage discrepancy (absolute percentage error)
        def percentage_error(predicted, actual):
            return abs(predicted - actual) / actual * 100

        mc_error = percentage_error(forecasts['predicted_price_mc'], actual_future_price)
        arima_error = percentage_error(forecasts['predicted_price_arima_garch'], actual_future_price)

        print("\nPercentage Error:")
        print(f"Monte Carlo: {mc_error:.2f}%")
        print(f"ARIMA-GARCH: {arima_error:.2f}%")
        print("="*50)

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    asset_symbol = "GOOGL"
    # The base period for training and then forecasting. (Adjust as needed)
    base_start_date = "2023-01-01"
    base_end_date = "2024-01-30"
    forecast_horizon = 38  # days

    # List the historical spans (in days) you want to test (for example, 1 year and 2 years)
    historical_spans = [365, 730]

    backtest_forecasts(asset_symbol, base_start_date, base_end_date,
                       forecast_horizon=forecast_horizon,
                       historical_spans=historical_spans)
