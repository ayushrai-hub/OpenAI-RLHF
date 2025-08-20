import math

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
