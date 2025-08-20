from datetime import date


# Actually we can't use requests? We must use Python to do GET requests? It's allowed. Let's use pandas.read_csv from the URL.

import pandas as pd

url_myr = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXMAUS'
url_sgd = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXSIUS'

myr = pd.read_csv(url_myr, parse_dates=['DATE'])
sgd = pd.read_csv(url_sgd, parse_dates=['DATE'])

# rename columns
myr.columns, sgd.columns
