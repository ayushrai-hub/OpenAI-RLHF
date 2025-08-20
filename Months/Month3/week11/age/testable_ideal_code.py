
def identify_middle_sibling(*relations: tuple[str, str, str]) -> str:
    R_XY, R_XZ, R_YZ = relations
    
    # Initialize a dictionary to store the age scores
    ages = {'X': 0, 'Y': 0, 'Z': 0}
    
    # Update age scores based on the relationship between X and Y
    if R_XY == '>':
        ages['X'] += 1
    elif R_XY == '<':
        ages['Y'] += 1
    
    # Update age scores based on the relationship between X and Z
    if R_XZ == '>':
        ages['X'] += 1
    elif R_XZ == '<':
        ages['Z'] += 1
    
    # Update age scores based on the relationship between Y and Z
    if R_YZ == '>':
        ages['Y'] += 1
    elif R_YZ == '<':
        ages['Z'] += 1
    
    # Sort siblings based on their scores
    sorted_siblings = sorted(ages, key=ages.get)
    
    # Return the sibling in the middle position
    return sorted_siblings[1]
