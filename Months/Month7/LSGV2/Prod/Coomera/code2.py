import requests

def geocode_arcgis(address):
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    params = {
        'f': 'json',
        'SingleLine': address,
        'outFields': 'Match_addr,Addr_type',
        'maxLocations': 1
    }
    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    if 'candidates' in data and data['candidates']:
        loc = data['candidates'][0]['location']
        return loc['y'], loc['x']  # lat, lon
    else:
        return None, None

for d in daycares:
    lat, lon = geocode_arcgis(d['address'])
    d['lat'] = lat
    d['lon'] = lon
    print(d['name'], d['lat'], d['lon'])
