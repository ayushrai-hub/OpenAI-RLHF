import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm

def backtest(asset_symbol, prediction_horizon, historical_spans, end_date):
    results = []

    for span in historical_spans:
        # Determine start date based on historical span
        start_date = pd.to_datetime(end_date) - pd.Timedelta(days=span)
        
        # Fetch historical data
        past_data = yf.download(asset_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date)
        if len(past_data) < 60:
            print(f"Not enough data for span {span} days. Skipping.")
            continue
        
        # Compute daily log returns
        daily_log_returns = np.log(past_data['Close'] / past_data['Close'].shift(1)).dropna()
        
        # Last known price from historical data
        starting_price = past_data['Close'].iloc[-1]

        # --------------------- Monte Carlo -------------------------
        simulations = 10000
        np.random.seed(24)
        simulated_prices = np.zeros((prediction_horizon, simulations))
        simulated_prices[0] = starting_price
        curr_volatility = daily_log_returns.std()
        vol_shock_intensity = 0.35
        peak_volatility = curr_volatility * 2

        for t in range(1, prediction_horizon):
            vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
            curr_volatility = np.abs(curr_volatility + vol_shock)
            curr_volatility = np.minimum(curr_volatility, peak_volatility)
            norm_returns = np.random.normal(daily_log_returns.mean() - (curr_volatility ** 2) / 2, 
                                            curr_volatility / np.sqrt(252), 
                                            simulations)
            simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)

        predicted_price_mc = simulated_prices[-1].mean()
        
        # ----------------- ARIMA-GARCH ----------------------------
        arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
        arima_result = arima_model.fit()
        arima_prediction = arima_result.forecast(steps=prediction_horizon)

        garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
        garch_result = garch_model.fit(disp='off')
        garch_forecast = garch_result.forecast(horizon=prediction_horizon)
        predicted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100

        predicted_log_return_sum = arima_prediction.sum()
        predicted_price_arima_garch = starting_price * np.exp(predicted_log_return_sum)

        # ------------- Obtain Actual Price --------------------------
        actual_start = pd.to_datetime(end_date)
        actual_end = actual_start + pd.Timedelta(days=prediction_horizon + 5)
        actual_data = yf.download(asset_symbol, start=actual_start.strftime('%Y-%m-%d'), end=actual_end.strftime('%Y-%m-%d'))
        if len(actual_data) < prediction_horizon:
            print(f"Not enough actual data after {end_date}. Skipping.")
            continue
        actual_price = actual_data['Close'].iloc[prediction_horizon - 1]

        # -------------- Performance Metrics --------------------------
        actual_direction = 'up' if actual_price >= starting_price else 'down'

        # Monte Carlo
        mc_direction = 'up' if predicted_price_mc >= starting_price else 'down'
        mc_direction_accuracy = (mc_direction == actual_direction)
        mc_error_pct = abs(predicted_price_mc - actual_price) / actual_price * 100

        # ARIMA-GARCH
        ag_direction = 'up' if predicted_price_arima_garch >= starting_price else 'down'
        ag_direction_accuracy = (ag_direction == actual_direction)
        ag_error_pct = abs(predicted_price_arima_garch - actual_price) / actual_price * 100

        results.append({
            'span_days': span,
            'model': 'Monte Carlo',
            'predicted_price': predicted_price_mc,
            'actual_price': actual_price,
            'direction_accuracy': mc_direction_accuracy,
            'percent_error': mc_error_pct
        })
        results.append({
            'span_days': span,
            'model': 'ARIMA-GARCH',
            'predicted_price': predicted_price_arima_garch,
            'actual_price': actual_price,
            'direction_accuracy': ag_direction_accuracy,
            'percent_error': ag_error_pct
        })

    # Present results
    results_df = pd.DataFrame(results)
    print("\nBacktest Results:")
    print(results_df)

    # Plotting Accuracy
    fig, ax = plt.subplots(figsize=(10,6))
    for model in results_df['model'].unique():
        subset = results_df[results_df['model'] == model]
        ax.plot(subset['span_days'], subset['percent_error'], label=model, marker='o')
    ax.set_title('Prediction Error by Historical Data Span')
    ax.set_xlabel('Historical Span (Days)')
    ax.set_ylabel('Percent Error')
    ax.legend()
    plt.show()

# ---------------- Call the Backtest Function ----------------------
historical_spans = [180, 240, 300, 360, 420]  # Different historical data spans
backtest(asset_symbol="GOOGL", prediction_horizon=38, historical_spans=historical_spans, end_date="2023-12-20")
