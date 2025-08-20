import requests

def geocode_geo_maps(address):
    url = "https://geocode.maps.co/search"
    params = {'q': address}
    headers = {'User-Agent': 'ChatGPT'}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    try:
        data = r.json()
    except Exception as e:
        print("Error parsing JSON", e, r.text[:100])
        return None, None
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None, None

for d in daycares:
    lat, lon = geocode_geo_maps(d['address'])
    print(d['name'], lat, lon)
