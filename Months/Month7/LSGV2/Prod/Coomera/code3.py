import math

central_lat = -27.8583
central_lon = 153.3167

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

for d in daycares:
    d['distance_km'] = haversine(central_lat, central_lon, d['lat'], d['lon'])

# average rating:
avg_rating = sum(d['rating'] for d in daycares) / len(daycares)

# farthest daycare:
farthest = max(daycares, key=lambda x: x['distance_km'])

avg_rating, farthest
