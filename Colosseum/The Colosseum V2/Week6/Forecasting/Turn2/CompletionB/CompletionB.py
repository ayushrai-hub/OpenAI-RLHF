import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from datetime import timedelta

# Backtesting function
def backtest_predictions(asset_symbol, end_date, historical_spans, forecast_horizon, simulations=10000):
    results = []

    for span_days in historical_spans:
        start_date = (pd.to_datetime(end_date) - timedelta(days=span_days)).strftime('%Y-%m-%d')
        future_end_date = (pd.to_datetime(end_date) + timedelta(days=forecast_horizon)).strftime('%Y-%m-%d')

        # Fetch historical and future actual data
        historical_data = yf.download(asset_symbol, start=start_date, end=end_date)
        future_actual_data = yf.download(asset_symbol, start=end_date, end=future_end_date)

        if len(historical_data) < 60 or len(future_actual_data) < forecast_horizon:
            print(f"Insufficient data for span {span_days} days. Skipping.")
            continue

        actual_end_price = future_actual_data['Close'].iloc[-1]
        actual_direction = np.sign(actual_end_price - historical_data['Close'].iloc[-1])

        # Compute log returns
        daily_log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1)).dropna()

        # Monte Carlo Simulation
        np.random.seed(24)
        simulated_prices = np.zeros((forecast_horizon, simulations))
        starting_price = historical_data['Close'].iloc[-1]
        simulated_prices[0] = starting_price

        curr_volatility = daily_log_returns.std()
        vol_shock_intensity = 0.35
        peak_volatility = curr_volatility * 2

        for t in range(1, forecast_horizon):
            vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
            curr_volatility = np.minimum(np.abs(curr_volatility + vol_shock), peak_volatility)
            norm_returns = np.random.normal(
                daily_log_returns.mean() - (curr_volatility ** 2) / 2,
                curr_volatility / np.sqrt(252),
                simulations)
            simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)

        predicted_price_mc = simulated_prices[-1].mean()
        predicted_direction_mc = np.sign(predicted_price_mc - starting_price)
        pct_error_mc = np.abs(predicted_price_mc - actual_end_price) / actual_end_price * 100
        direction_correct_mc = predicted_direction_mc == actual_direction

        # ARIMA-GARCH Forecast
        try:
            # ARIMA Prediction
            arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
            arima_result = arima_model.fit()
            arima_pred_returns = arima_result.forecast(forecast_horizon).sum()

            # GARCH Prediction
            garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
            garch_result = garch_model.fit(disp='off')
            garch_vol_pred = np.sqrt(garch_result.forecast(horizon=forecast_horizon).variance.values[-1, :]) / 100

            predicted_price_arima_garch = starting_price * np.exp(arima_pred_returns / 100)
            predicted_direction_ag = np.sign(predicted_price_arima_garch - starting_price)
            pct_error_ag = np.abs(predicted_price_arima_garch - actual_end_price) / actual_end_price * 100
            direction_correct_ag = predicted_direction_ag == actual_direction
        except Exception as e:
            print(f"ARIMA-GARCH failed for span {span_days} days: {e}")
            predicted_price_arima_garch = np.nan
            direction_correct_ag = False
            pct_error_ag = np.nan

        # Store results
        results.append({
            'Historical_span_days': span_days,
            'Actual_Price': actual_end_price,
            'MC_Price': predicted_price_mc,
            'MC_Direction_Correct': direction_correct_mc,
            'MC_Percentage_Error': pct_error_mc,
            'ARIMA_GARCH_Price': predicted_price_arima_garch,
            'ARIMA_GARCH_Direction_Correct': direction_correct_ag,
            'ARIMA_GARCH_Percentage_Error': pct_error_ag
        })

        print(f"\nSpan {span_days} days Results:")
        print(f"Actual Price after {forecast_horizon} days: ${actual_end_price:.2f}")
        print(f"Monte Carlo Prediction: ${predicted_price_mc:.2f}, Direction Correct: {direction_correct_mc}, "
              f"Percentage Error: {pct_error_mc:.2f}%")
        print(f"ARIMA-GARCH Prediction: ${predicted_price_arima_garch:.2f}, Direction Correct: {direction_correct_ag}, "
              f"Percentage Error: {pct_error_ag:.2f}%")

    return pd.DataFrame(results)

# Running backtests
asset_symbol = "GOOGL"
end_date = "2024-01-30"
historical_spans = [180, 240, 365, 540, 730]  # 6m, 8m, 1y, 1.5y, 2y
forecast_horizon = 38  # days

results_df = backtest_predictions(asset_symbol, end_date, historical_spans, forecast_horizon)

# Visualize comparative results
results_df.set_index('Historical_span_days', inplace=True)
results_df[['MC_Percentage_Error', 'ARIMA_GARCH_Percentage_Error']].plot(
    kind='bar', figsize=(10, 6), title='Percentage Error: Monte Carlo vs ARIMA-GARCH')
plt.ylabel('Percentage Error (%)')
plt.xlabel('Historical Span (Days)')
plt.xticks(rotation=0)
plt.grid(True, alpha=0.2)
plt.show()

# Direction accuracy comparison
direction_accuracy = results_df[['MC_Direction_Correct', 'ARIMA_GARCH_Direction_Correct']].mean() * 100
direction_accuracy.plot(kind='bar', figsize=(8, 6), title='Direction Accuracy (%)')
plt.ylabel('Accuracy (%)')
plt.xticks(rotation=0)
plt.grid(True, alpha=0.2)
plt.show()
