import numpy as np
from scipy.sparse import lil_matrix

def create_sparse_interaction_matrix(interactions):
    users = [user for user, item in interactions]
    items = [item for user, item in interactions]
    num_users = max(users) + 1  # Assuming user indices start at 0
    num_items = max(items) + 1  # Assuming item indices start at 0

    # Create a sparse matrix with the specified shape
    interaction_matrix = lil_matrix((num_users, num_items), dtype=bool)

    for user, item in interactions:
        interaction_matrix[user, item] = True

    return interaction_matrix, num_users, num_items
