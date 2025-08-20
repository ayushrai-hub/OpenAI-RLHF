# Load the file for one year
import pandas as pd

year = 2022
url = f'https://www.ndbc.noaa.gov/view_text_file.php?filename=44013h{year}.txt.gz&dir=data/historical/stdmet/'
df = pd.read_csv(url, delim_whitespace=True, comment='#', header=None, na_values=['99.00','99','999.0','999','MM'])
df.head()

col_names = ['YYYY','MM','DD','hh','mm','WDIR','WSPD','GST','WVHT','DPD','APD','MWD','PRES','ATMP','WTMP','DEWP','VIS','TIDE']
df.columns = col_names
df.head()

years = list(range(2013, 2023))  # 2013 to 2022 inclusive
dfs = []
for year in years:
    url = f'https://www.ndbc.noaa.gov/view_text_file.php?filename=44013h{year}.txt.gz&dir=data/historical/stdmet/'
    try:
        df_year = pd.read_csv(url, delim_whitespace=True, comment='#', header=None, na_values=['99.00','99','999.0','999'])
        df_year.columns = col_names
        df_year['YYYY'] = year  # to ensure the year is correct
        dfs.append(df_year)
        print(f"Loaded {year}, shape={df_year.shape}")
    except Exception as e:
        print(f"Failed {year}: {e}")

# Concatenate
all_data = pd.concat(dfs, ignore_index=True)
print(all_data.shape)

# Filter for January and valid values
jan_data = all_data[all_data['MM'] == 1]
# We need both WSPD and WVHT columns
valid_data = jan_data.dropna(subset=['WSPD', 'WVHT'])
# Compute overall means
avg_wspd = valid_data['WSPD'].mean()
avg_wvht = valid_data['WVHT'].mean()
print("January (2013-2022): Average WSPD =", avg_wspd, "m/s")
print("January (2013-2022): Average WVHT =", avg_wvht, "m")

# Compute per-year averages for January
per_year = valid_data.groupby('YYYY').agg({'WSPD':'mean','WVHT':'mean'})
per_year

avg_wspd_yearly = per_year['WSPD'].mean()
avg_wvht_yearly = per_year['WVHT'].mean()
print(avg_wspd_yearly, avg_wvht_yearly)

print(round(avg_wspd_yearly,2), round(avg_wvht_yearly,2))

