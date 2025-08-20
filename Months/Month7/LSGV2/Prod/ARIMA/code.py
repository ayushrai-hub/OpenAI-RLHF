import pandas as pd

# Fetch the two series
import requests

# Actually we can't use requests? We must use Python to do GET requests? It's allowed. Let's use pandas.read_csv from the URL.

import pandas as pd

url_myr = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXMAUS'
url_sgd = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXSIUS'

myr = pd.read_csv(url_myr, parse_dates=['DATE'])
sgd = pd.read_csv(url_sgd, parse_dates=['DATE'])

# rename columns
myr.columns, sgd.columns
import requests

# fetch a sample of the file
print(pd.read_csv(url_myr, nrows=5).head())
print(pd.read_csv(url_myr, nrows=5).columns)

myr = pd.read_csv(url_myr, parse_dates=['observation_date'])
sgd = pd.read_csv(url_sgd, parse_dates=['observation_date'])

# rename columns more friendly
myr.rename(columns={'observation_date':'DATE', 'DEXMAUS':'MYR_per_USD'}, inplace=True)
sgd.rename(columns={'observation_date':'DATE', 'DEXSIUS':'SGD_per_USD'}, inplace=True)

# Merge on DATE
merged = pd.merge(sgd, myr, on='DATE', how='inner')

# Compute SGD per MYR: = (SGD per USD) / (MYR per USD)
merged['SGD_per_MYR'] = merged['SGD_per_USD'] / merged['MYR_per_USD']

# Last 5 rows
merged.tail()

merged['MYR_per_SGD'] = merged['MYR_per_USD'] / merged['SGD_per_USD']
merged.tail()
from datetime import datetime, timedelta

end_date = pd.Timestamp('today').normalize()  # 2025-03-17
start_date = end_date - pd.DateOffset(years=10)

last10 = merged[(merged['DATE'] >= start_date) & (merged['DATE'] <= end_date)][['DATE', 'MYR_per_SGD']]

last10.head(), last10.tail(), last10.shape
import matplotlib.pyplot as plt

# we can skip the plot for the user because not necessary.
# Check stationarity by differencing and ADF test.

from statsmodels.tsa.stattools import adfuller

# original
result = adfuller(last10['MYR_per_SGD'].dropna())
print('ADF statistic:', result[0], 'p-value:', result[1])

# first difference
result_diff = adfuller(last10['MYR_per_SGD'].diff().dropna())
print('ADF diff statistic:', result_diff[0], 'p-value:', result_diff[1])

from statsmodels.tsa.arima.model import ARIMA

# Fit ARIMA(1,1,1)
model = ARIMA(last10['MYR_per_SGD'], order=(1,1,1))
res = model.fit()
print(res.summary())
# Build time series with date index
ts = last10.set_index('DATE')['MYR_per_SGD']

# Fit ARIMA(1,1,1)
model2 = ARIMA(ts, order=(1,1,1))
res2 = model2.fit()

# Now we can predict for a specific date
target_date = '2024-12-31'
pred = res2.get_prediction(start=target_date, end=target_date)
print(pred.predicted_mean)
print("se", pred.se_mean)
conf_int = pred.conf_int()
print(conf_int)
a