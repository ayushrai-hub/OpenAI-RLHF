import requests
import csv
from io import StringIO

# Fetch ACFTREF.txt
url_ref = 'https://raw.githubusercontent.com/simonw/scrape-faa-releasable-aircraft/main/ACFTREF.txt'
resp = requests.get(url_ref)
text = resp.content.decode('utf-8', errors='ignore')
# parse CSV
f = StringIO(text)
reader = csv.DictReader(f)
codes = []
for row in reader:
    if row['MFR'].strip().upper() == 'BOEING' and '737' in row['MODEL']:
        codes.append((row['CODE'], row['MODEL']))
# Print number and some codes
len(codes), codes[:20]
