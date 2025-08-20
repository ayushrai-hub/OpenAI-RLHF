import numpy as np  
import pandas as pd  
import yfinance as yf  
from matplotlib import pyplot as plt  
from statsmodels.tsa.arima.model import ARIMA  
from arch import arch_model  
from scipy.stats import norm  
from arch.__future__ import reindexing  

# Fetch historical data  
ticker_symbol = "LDOS"  
historical_data = yf.download(ticker_symbol, start="2023-04-01", end="2024-04-09")  
original_end_date = "2024-04-09"  # Used for extending the end date by 30 days later  

# Calculate daily log returns  
log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))  
log_returns.dropna(inplace=True)  
log_returns.index = pd.DatetimeIndex(log_returns.index).to_period('D')  

# Monte Carlo simulation parameters  
time_horizon = 38  # Days  
num_simulations = 10000  
initial_price = historical_data['Close'].iloc[-1]  

# Prepare for simulation  
np.random.seed(42)  
price_paths = np.zeros((time_horizon, num_simulations))  
price_paths[0] = initial_price  

# Implementing Stochastic Volatility adjustments with a realistic volatility shock cap  
volatility = log_returns.std()  
vol_volatility = 0.4  
max_volatility = volatility * 2  

for t in range(1, time_horizon):  
    vol_shock = np.random.normal(0, vol_volatility, num_simulations)  
    volatility = np.abs(volatility + vol_shock)  
    volatility = np.minimum(volatility, max_volatility)  

    normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2,  
                                      volatility / np.sqrt(252),
                                      num_simulations)  
    price_paths[t] = price_paths[t - 1] * np.exp(normal_returns)  

# Monte Carlo simulation plot  
plt.figure(figsize=(10, 6))  
for i in range(num_simulations):  
    plt.plot(price_paths[:, i], linewidth=0.5, alpha=0.2, color='gray')  
plt.plot(price_paths.mean(axis=1), color='red', linewidth=2, label='Average Path')  
plt.title(f"Monte Carlo Simulation of {ticker_symbol} Over {time_horizon} Days")  
plt.xlabel("Days")  
plt.ylabel("Price")  
plt.legend()  
plt.show()  

forecasted_price_mc = price_paths[-1].mean()  
print(f"The forecasted price of {ticker_symbol} {time_horizon} days out is approximately: ${forecasted_price_mc:.2f}")  

confidence_level_mc = 0.95  
sorted_prices_mc = np.sort(price_paths[-1])  
VaR_mc = np.percentile(sorted_prices_mc, (1 - confidence_level_mc) * 100)  
ES_mc = sorted_prices_mc[sorted_prices_mc <= VaR_mc].mean()  
print(f"Monte Carlo VaR (95% confidence): ${VaR_mc:.2f}")  
print(f"Monte Carlo Expected Shortfall: ${ES_mc:.2f}")  

arima_model = ARIMA(log_returns, order=(10, 0, 1))  
arima_result = arima_model.fit()  
arima_forecast = arima_result.forecast(steps=38)  

garch_model = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1)  
garch_result = garch_model.fit(update_freq=5, disp='off')  
garch_forecast = garch_result.forecast(horizon=38)  
forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100  

forecasted_log_return = arima_forecast.sum()  
forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)  
print(f"Forecasted price using ARIMA-GARCH: ${forecasted_price_arima_garch:.2f}")  

confidence_level = 0.95  
z_score = norm.ppf(confidence_level)  

VaR_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1]))  
ES_arima_garch = initial_price - (initial_price * np.exp(-z_score * forecasted_volatility[-1] / (1 - confidence_level)))  
print(f"VaR using ARIMA-GARCH (95% confidence): ${VaR_arima_garch:.2f}")  
print(f"Expected Shortfall using ARIMA-GARCH: ${ES_arima_garch:.2f}")  

# ------------------- Backtesting Enhancements -------------------

def backtest_forecasting(ticker, base_end_date, historical_sizes, horizon=30):
    results = []

    for size in historical_sizes:
        start_date = pd.to_datetime(base_end_date) - pd.Timedelta(days=size)  
        end_date = base_end_date

        historical_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date)  
        log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))  
        log_returns.dropna(inplace=True)
        
        initial_price = historical_data['Close'].iloc[-1]

        # Monte Carlo Simulation Forecast
        num_simulations = 10000
        volatility = log_returns.std()
        np.random.seed(42)
        price_paths = np.zeros((horizon, num_simulations))
        price_paths[0] = initial_price

        for t in range(1, horizon):
            vol_shock = np.random.normal(0, 0.4, num_simulations)
            volatility = np.abs(volatility + vol_shock)
            volatility = np.minimum(volatility, volatility.std() * 2)

            normal_returns = np.random.normal(log_returns.mean() - (volatility ** 2) / 2,  
                                              volatility / np.sqrt(252), num_simulations)
            price_paths[t] = price_paths[t-1] * np.exp(normal_returns)
        
        forecasted_price_mc = price_paths[-1].mean()

        # ARIMA-GARCH Combined Forecast
        arima_result = ARIMA(log_returns, order=(10, 0, 1)).fit()
        arima_forecast = arima_result.forecast(steps=horizon)
        
        garch_result = arch_model(log_returns*100, mean='Zero', vol='Garch', p=1, q=1).fit(update_freq=5, disp='off')
        garch_forecast = garch_result.forecast(horizon=horizon)
        forecasted_volatility = np.sqrt(garch_forecast.variance.values[-1, :]) / 100
        
        forecasted_log_return = arima_forecast.sum()
        forecasted_price_arima_garch = initial_price * np.exp(forecasted_log_return / 100)

        # Actual price after horizon days for comparison
        actual_prices = yf.download(ticker, start=end_date, end=(pd.to_datetime(end_date) + pd.Timedelta(days=horizon)).strftime('%Y-%m-%d'))
        actual_price_horizon = actual_prices['Close'].iloc[-1] if not actual_prices.empty else np.nan
        
        if not np.isnan(actual_price_horizon):
            direction_mc = int((forecasted_price_mc - initial_price) > 0) == int((actual_price_horizon - initial_price) > 0)
            direction_arima_garch = int((forecasted_price_arima_garch - initial_price) > 0) == int((actual_price_horizon - initial_price) > 0)
            
            error_mc = abs((forecasted_price_mc - actual_price_horizon) / actual_price_horizon) * 100
            error_arima_garch = abs((forecasted_price_arima_garch - actual_price_horizon) / actual_price_horizon) * 100
            
            results.append({
                'Historical Size': size,
                'Monte Carlo Direction Accurate': direction_mc,
                'Monte Carlo Error (%)': error_mc,
                'ARIMA-GARCH Direction Accurate': direction_arima_garch,
                'ARIMA-GARCH Error (%)': error_arima_garch
            })

    backtest_df = pd.DataFrame(results)
    print(backtest_df)

# Run Backtesting
backtest_forecasting(ticker_symbol, original_end_date, [365, 730, 1095], horizon=30)
