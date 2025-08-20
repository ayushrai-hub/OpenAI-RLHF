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
