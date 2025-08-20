# ideal_completion.py

import math
import requests

def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface given their latitude and longitude in degrees.
    Returns the distance in meters.
    """
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0)) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def calculate_initial_compass_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the initial compass bearing (in degrees) from point A to point B.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon_rad = math.radians(lon2 - lon1)

    x = math.sin(delta_lon_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad)

    initial_bearing_rad = math.atan2(x, y)
    initial_bearing_deg = (math.degrees(initial_bearing_rad) + 360) % 360

    return initial_bearing_deg

def compute_pixel_coords(
    drone_lat: float, drone_lon: float, drone_alt: float,
    drone_pitch: float, drone_roll: float, drone_yaw: float,
    obj_lat: float, obj_lon: float,
    img_width: int, img_height: int,
    horiz_fov: float, vert_fov: float
) -> tuple[int, int]:
    """
    Computes the pixel coordinates (x, y) of an object in the drone's camera image frame.
    Returns a tuple (pixel_x, pixel_y) indicating the object's position in the image.
    """
    pitch_rad = math.radians(drone_pitch)
    roll_rad = math.radians(drone_roll)
    yaw_rad = math.radians(drone_yaw)

    # Step 1: Calculate distance and bearing
    distance = calculate_haversine(drone_lat, drone_lon, obj_lat, obj_lon)
    bearing = calculate_initial_compass_bearing(drone_lat, drone_lon, obj_lat, obj_lon)

    # Step 2: Relative bearing and object position in the drone's local frame
    relative_bearing = math.radians((bearing - drone_yaw + 360) % 360)

    x_relative = distance * math.sin(relative_bearing)
    y_relative = distance * math.cos(relative_bearing)
    z_relative = -drone_alt  # Assuming ground-level object, altitude difference is negative

    # Step 3: Apply pitch and roll rotations
    x_rotated = x_relative
    y_rotated = y_relative * math.cos(pitch_rad) - z_relative * math.sin(pitch_rad)
    z_rotated = y_relative * math.sin(pitch_rad) + z_relative * math.cos(pitch_rad)

    x_camera = x_rotated * math.cos(roll_rad) + z_rotated * math.sin(roll_rad)
    y_camera = y_rotated
    z_camera = -x_rotated * math.sin(roll_rad) + z_rotated * math.cos(roll_rad)

    # Step 4: Handle objects behind the camera
    if y_camera <= 0:  # Object is not visible
        return img_width // 2, img_height - 1  # Default position

    # Step 5: Calculate angles in the camera's field of view
    horiz_angle = math.atan2(x_camera, y_camera)
    vert_angle = math.atan2(z_camera, math.sqrt(x_camera ** 2 + y_camera ** 2))

    # Step 6: Clamp angles to FOV limits
    horiz_angle = max(-math.radians(horiz_fov / 2), min(math.radians(horiz_fov / 2), horiz_angle))
    vert_angle = max(-math.radians(vert_fov / 2), min(math.radians(vert_fov / 2), vert_angle))

    # Step 7: Map angles to pixel coordinates
    pixel_x = (horiz_angle / math.radians(horiz_fov / 2)) * (img_width / 2) + (img_width / 2)
    pixel_y = (1 - (vert_angle / math.radians(vert_fov / 2))) * (img_height / 2)

    # Clamp pixel values to image dimensions
    pixel_x = max(0, min(img_width - 1, pixel_x))
    pixel_y = max(0, min(img_height - 1, pixel_y))

    return int(pixel_x), int(pixel_y)

def nearby_roads(latitude: float, longitude: float, rad: int = 50) -> list[dict]:
    """
    Fetches nearby roads from OpenStreetMap using Overpass API.
    Returns a list of dictionaries with road names and coordinates.
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      way(around:{rad},{latitude},{longitude})["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|pedestrian|track|path|footway|cycleway)$"];
    );
    out geom;
    """
    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        response.raise_for_status()
        data = response.json()
        roads = []
        for element in data.get('elements', []):
            if element.get('type') == 'way':
                road_name = element.get('tags', {}).get('name')
                if road_name:
                    coordinates = [(node['lat'], node['lon']) for node in element.get('geometry', [])]
                    roads.append({"name": road_name, "coordinates": coordinates})
        return roads
    except requests.RequestException:
        return []