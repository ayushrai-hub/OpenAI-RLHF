import math

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
    
    return M, circle_radius
