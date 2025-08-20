import math

def spheres_intersect(C1, C2, r1, r2):
    # Calculate the distance between the centers
    d = math.dist(C1, C2)
    
    # Check intersection conditions
    if d > (r1 + r2):
        # Spheres are too far apart, no intersection
        return False
    elif d < abs(r1 - r2):
        # One sphere is inside the other without intersection
        return False
    else:
        # Spheres intersect
        return True

def intersection_circle(C1, C2, r1, r2):
    d = math.dist(C1, C2)

    # Step 2: Find the distance 'a' from C1 to the plane of intersection
    a = (r12 - r22 + d2) / (2 * d)
    
    # Step 3: Find the radius 'r' of the intersection circle
    circle_radius = math.sqrt(abs(r12 - a2))  # Use abs to avoid negative sqrt due to floating-point errors
    
    # Step 4: Find the midpoint 'M' of the intersection circle
    # Vector from C1 to C2
    C1C2 = (C2[0] - C1[0], C2[1] - C1[1], C2[2] - C1[2])
    
    # Normalize C1C2
    length = math.sqrt(C1C2[0]2 + C1C2[1]2 + C1C2[2]2)
    C1C2_norm = (C1C2[0] / length, C1C2[1] / length, C1C2[2] / length)
    
    # Point M is at a distance 'a' along the line from C1
    M = (C1[0] + a * C1C2_norm[0],
         C1[1] + a * C1C2_norm[1],
         C1[2] + a * C1C2_norm[2])
    
    return M, circle_radius, C1C2_norm

def circle_points(M, N, circle_radius, num_points=20):
    points = []
    
    # If N is the normal, we need vectors in the plane:
    # Start with a guess vector
    if abs(N[0]) < abs(N[1]):
        guess = (1, 0, 0)
    else:
        guess = (0, 1, 0)
    
    # Using Gram-Schmidt to find a vector orthonormal to N
    dot = guess[0] * N[0] + guess[1] * N[1] + guess[2] * N[2]
    orth1 = (guess[0] - dot * N[0],
             guess[1] - dot * N[1],
             guess[2] - dot * N[2])
    len_orth1 = math.sqrt(orth1[0]2 + orth1[1]2 + orth1[2]2)
    if len_orth1 == 0:
        # If guess is parallel to N, pick a different guess vector
        guess = (0, 0, 1)
        dot = guess[0] * N[0] + guess[1] * N[1] + guess[2] * N[2]
        orth1 = (guess[0] - dot * N[0],
                 guess[1] - dot * N[1],
                 guess[2] - dot * N[2])
        len_orth1 = math.sqrt(orth1[0]2 + orth1[1]2 + orth1[2]2)
    # Normalize orth1
    orth1 = (orth1[0] / len_orth1, orth1[1] / len_orth1, orth1[2] / len_orth1)
    
    # Find second orthonormal vector using cross product
    orth2 = (N[1] * orth1[2] - N[2] * orth1[1],
             N[2] * orth1[0] - N[0] * orth1[2],
             N[0] * orth1[1] - N[1] * orth1[0])
    
    # Generate points on the circle
    for i in range(num_points):
        theta = 2 * math.pi * i / num_points
        x = M[0] + circle_radius * (orth1[0] * math.cos(theta) + orth2[0] * math.sin(theta))
        y = M[1] + circle_radius * (orth1[1] * math.cos(theta) + orth2[1] * math.sin(theta))
        z = M[2] + circle_radius * (orth1[2] * math.cos(theta) + orth2[2] * math.sin(theta))
        points.append((x, y, z))
    return points

def format_coordinates(points, identifier_prefix="POINT"):
    formatted_points = []
    for i, (x, y, z) in enumerate(points, start=1):
        formatted_points.append(f"COORD:{identifier_prefix}{i}:{x}:{y}:{z}:#FFFF00BA:")
    return formatted_points

# Example usage:
if __name__ == "__main__":
    # Example centers and radii
    C1 = (0, 0, 0)
    r1 = 5
    C2 = (3, 4, 0)
    r2 = 5

    if not spheres_intersect(C1, C2, r1, r2):
        print("The spheres do not intersect.")
    else:
        M, circ_radius, normal = intersection_circle(C1, C2, r1, r2)
        points_on_circle = circle_points(M, normal, circ_radius, 20)
        formatted_points = format_coordinates(points_on_circle, "INTERSECTION")
        for p in formatted_points:
            print(p)
