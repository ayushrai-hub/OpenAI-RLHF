import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from scipy.stats import norm
from arch.__future__ import reindexing

def run_monte_carlo(daily_log_returns, starting_price, horizon=38, simulations=10000, seed=24):
    np.random.seed(seed)
    simulated_prices = np.zeros((horizon, simulations))
    simulated_prices[0] = starting_price

    # Parameters for simulation
    curr_volatility = daily_log_returns.std()
    vol_shock_intensity = 0.35  # Volatility of volatility
    peak_volatility = curr_volatility * 2  # Maximum volatility threshold

    for t in range(1, horizon):
        vol_shock = np.random.normal(0, vol_shock_intensity, simulations)
        curr_volatility = np.abs(curr_volatility + vol_shock)
        curr_volatility = np.minimum(curr_volatility, peak_volatility)

        norm_returns = np.random.normal(
            daily_log_returns.mean() - (curr_volatility ** 2) / 2,
            curr_volatility / np.sqrt(252),
            simulations
        )
        simulated_prices[t] = simulated_prices[t - 1] * np.exp(norm_returns)
        
    predicted_price_mc = simulated_prices[-1].mean()
    sorted_prices_mc = np.sort(simulated_prices[-1])
    confidence_interval_mc = 0.95
    VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_interval_mc) * 100)
    ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()
    
    return predicted_price_mc, VaR_mc, ES_mc, simulated_prices

def run_arima_garch(daily_log_returns, starting_price, horizon=38):
    # ARIMA for the log returns forecast
    arima_model = ARIMA(daily_log_returns, order=(5, 0, 2))
    arima_result = arima_model.fit()
    arima_prediction = arima_result.forecast(steps=horizon)  # Forecast horizon steps

    # GARCH for volatility forecast, scaling returns by 100
    garch_model = arch_model(daily_log_returns * 100, mean='Zero', vol='Garch', p=1, q=1)
    garch_result = garch_model.fit(update_freq=5, disp='off')
    garch_prediction = garch_result.forecast(horizon=horizon)
    predicted_volatility = np.sqrt(garch_prediction.variance.values[-1, :]) / 100

    # Combine the forecasts: sum ARIMA prediction to get a cumulative log return forecast
    predicted_log_return = arima_prediction.sum()
    predicted_price_arima_garch = starting_price * np.exp(predicted_log_return / 100)

    # Calculate VaR and ES for ARIMA-GARCH using predicted volatility
    confidence_interval = 0.95
    z_value = norm.ppf(confidence_interval)
    VaR_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1]))
    ES_arima_garch = starting_price - (starting_price * np.exp(-z_value * predicted_volatility[-1] / (1 - confidence_interval)))
    
    return predicted_price_arima_garch, VaR_arima_garch, ES_arima_garch

def backtest_forecasts(asset_symbol, historical_end, forecast_horizon=38, simulations=10000, historical_spans_days=[365,730]):
    """
    For each historical span, re-run forecasts and then backtest by comparing to the actual outcome 38 days later.
    
    historical_end : end date for historical data window as a string ("YYYY-MM-DD")
    historical_spans_days : list of integers with the number of past days to consider.
    """
    
    results = []
    for span in historical_spans_days:
        # Define start date based on the span
        end_date = pd.to_datetime(historical_end)
        start_date = end_date - pd.Timedelta(days=span)
        
        # Fetch historical data for the specified span
        data = yf.download(asset_symbol, start=start_date.strftime('%Y-%m-%d'), end=historical_end)
        if data.empty:
            print(f"No data for span {span} days")
            continue
        # Compute daily log returns
        daily_log_returns = np.log(data['Close'] / data['Close'].shift(1))
        daily_log_returns.dropna(inplace=True)
        daily_log_returns.index = pd.DatetimeIndex(daily_log_returns.index).to_period('D')
        
        starting_price = data['Close'].iloc[-1]
        
        # Run Monte Carlo simulation forecast
        mc_price, mc_var, mc_es, mc_sim = run_monte_carlo(daily_log_returns, starting_price, horizon=forecast_horizon, simulations=simulations)
        
        # Run ARIMA-GARCH forecast
        arima_garch_price, arima_garch_var, arima_garch_es = run_arima_garch(daily_log_returns, starting_price, horizon=forecast_horizon)
        
        # Fetch actual future price (forecast_horizon days after historical_end)
        future_end_date = pd.to_datetime(historical_end) + pd.Timedelta(days=forecast_horizon)
        future_data = yf.download(asset_symbol, start=historical_end, end=future_end_date.strftime('%Y-%m-%d'))
        if future_data.empty:
            print(f"No future data available for evaluation for span {span} days.")
            continue
        actual_price = future_data['Close'].iloc[-1]
        
        # Compute metrics:
        # 1. Direction: Up or Down movement relative to the starting_price
        actual_direction = np.sign(actual_price - starting_price)
        mc_direction = np.sign(mc_price - starting_price)
        arima_garch_direction = np.sign(arima_garch_price - starting_price)
        
        # 2. Percentage error
        mc_error = 100 * np.abs((mc_price - actual_price) / actual_price)
        arima_garch_error = 100 * np.abs((arima_garch_price - actual_price) / actual_price)
        
        result = {
            'Historical_Span_Days': span,
            'Starting_Price': starting_price,
            'Actual_Price': actual_price,
            'MC_Predicted_Price': mc_price,
            'ARIMA_GARCH_Predicted_Price': arima_garch_price,
            'MC_Direction_Correct': (actual_direction == mc_direction),
            'ARIMA_GARCH_Direction_Correct': (actual_direction == arima_garch_direction),
            'MC_Percentage_Error': mc_error,
            'ARIMA_GARCH_Percentage_Error': arima_garch_error,
            'MC_VaR': mc_var,
            'MC_ES': mc_es,
            'ARIMA_GARCH_VaR': arima_garch_var,
            'ARIMA_GARCH_ES': arima_garch_es,
        }
        results.append(result)
        
        print("\nBacktest results for historical span (days):", span)
        print("-----------------------------------------------------")
        print(f"Starting Price: ${starting_price:.2f}")
        print(f"Actual Price after {forecast_horizon} days: ${actual_price:.2f}")
        print(f"Monte Carlo Predicted Price: ${mc_price:.2f}")
        print(f"ARIMA-GARCH Predicted Price: ${arima_garch_price:.2f}")
        print(f"Monte Carlo Direction Correct: {result['MC_Direction_Correct']}")
        print(f"ARIMA-GARCH Direction Correct: {result['ARIMA_GARCH_Direction_Correct']}")
        print(f"Monte Carlo Percentage Error: {mc_error:.2f}%")
        print(f"ARIMA-GARCH Percentage Error: {arima_garch_error:.2f}%")
        print(f"Monte Carlo VaR (95% CI): ${mc_var:.2f}")
        print(f"Monte Carlo ES (95% CI): ${mc_es:.2f}")
        print(f"ARIMA-GARCH VaR (95% CI): ${arima_garch_var:.2f}")
        print(f"ARIMA-GARCH ES (95% CI): ${arima_garch_es:.2f}")
        
    return pd.DataFrame(results)


# Running the backtesting function with two historical spans (example: 1 year and 2 years)
df_results = backtest_forecasts("GOOGL", historical_end="2024-01-30", forecast_horizon=38, simulations=10000, historical_spans_days=[365, 730])

# You can also visualize the results if needed
print("\nBacktesting Summary:")
print(df_results)
