import numpy as np
from scipy.sparse import lil_matrix

def create_sparse_interaction_matrix(interactions):
    if not interactions:
        return lil_matrix((0, 0)), 0, 0
    
    users, items = zip(*interactions)
    num_users = max(users) + 1
    num_items = max(items) + 1
    
    interaction_matrix = lil_matrix((num_users, num_items), dtype=bool)
    
    for user, item in interactions:
        interaction_matrix[user, item] = True
    
    return interaction_matrix, num_users, num_items

# Example usage
interactions = [(0, 1), (0, 2), (1, 2), (3, 4)]
matrix, users, items = create_sparse_interaction_matrix(interactions)

# Print the matrix as a dense array for visualization
print(matrix.toarray())
print(f"Number of users: {users}, Number of items: {items}")