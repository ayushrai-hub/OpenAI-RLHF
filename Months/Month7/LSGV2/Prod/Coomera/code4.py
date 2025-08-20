# We'll define the daycare data:
daycares = [
    {"name": "Play and Learn Early Learning Centre Upper Coomera", "rating": 4.0, "address": "577 Reserve Rd, Upper Coomera, QLD 4209, Australia"},
    {"name": "Story House Early Learning Coomera", "rating": 5.0, "address": "180 Old Coach Road, Upper Coomera, QLD 4209, Australia"},
    {"name": "Beattie Road Early Childhood Education Centre", "rating": 5.0, "address": "74 Beattie Road, Coomera, QLD 4209, Australia"},
    {"name": "Kidi Kingdom Child Care at Coomera", "rating": 5.0, "address": "87 Brygon Creek Drive, Upper Coomera, QLD 4209, Australia"},
    {"name": "Cubby Care Early Learning Centre Coomera", "rating": 4.3, "address": "10 Jemima Pl, Upper Coomera, QLD 4209, Australia"},
    {"name": "Sparrow Early Learning Upper Coomera", "rating": 5.0, "address": "228 Billinghurst Cres, Upper Coomera, QLD 4209, Australia"},
]

# We'll use Nominatim API to get coordinates. Let's define a helper to query the API with given address.

import requests

def geocode(address):
    # Use Nominatim OpenStreetMap API
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'ChatGPT'}
    # Do a get request:
    r = requests.get(base_url, params=params, headers=headers, timeout=30)
    data = r.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None, None

# Let's geocode each daycare:
for d in daycares:
    lat, lon = geocode(d['address'])
    d['lat'] = lat
    d['lon'] = lon

daycares
