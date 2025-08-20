import numpy as np

def compute_intersection_circle(P1, r1, P2, r2):
    # Convert points to numpy arrays
    P1 = np.array(P1, dtype=float)
    P2 = np.array(P2, dtype=float)

    # Compute the distance between centers
    d = np.linalg.norm(P2 - P1)

    # Check if the spheres intersect
    if d > r1 + r2 or d < abs(r1 - r2):
        print("The spheres do not intersect.")
        return None, None, None

    # Compute ex, ey, ez
    ex = (P2 - P1) / d

    # Compute the point where the line through the sphere intersection points crosses the line between the sphere centers
    t = (r12 - r22 + d2) / (2 * d)
    P3 = P1 + ex * t

    # Compute the radius of the circle
    h = np.sqrt(r12 - t2)

    # Find a vector orthogonal to ex
    if ex[0] != 0 or ex[1] != 0:
        temp = np.array([-ex[1], ex[0], 0])
    else:
        temp = np.array([0, -ex[2], ex[1]])
    ey = np.cross(ex, temp)
    ey /= np.linalg.norm(ey)

    ez = np.cross(ex, ey)

    # Generate 20 evenly spaced points around the circle
    angles = np.linspace(0, 2 * np.pi, 20, endpoint=False)
    points = []
    for angle in angles:
        point = P3 + h * (np.cos(angle) * ey + np.sin(angle) * ez)
        points.append(point)

    return points

def format_coordinates(points):
    formatted_points = []
    for idx, point in enumerate(points, start=1):
        x, y, z = point
        coord_str = f"COORD:{idx}:{x}:{y}:{z}:#FFFF00BA:"
        formatted_points.append(coord_str)
    return formatted_points

# Example input
P1 = [0, 0, 0]
r1 = 5
P2 = [3, 0, 0]
r2 = 5

# Compute the circle of intersection
points = compute_intersection_circle(P1, r1, P2, r2)

# If spheres intersect, format and print the coordinates
if points:
    formatted_points = format_coordinates(points)
    for coord in formatted_points:
        print(coord)
