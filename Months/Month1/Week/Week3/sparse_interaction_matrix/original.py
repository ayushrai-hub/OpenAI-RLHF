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

# Example usage:
interactions = [(0, 1), (0, 2), (1, 2), (3, 4)]
interaction_matrix, num_users, num_items = create_sparse_interaction_matrix(interactions)

# To print the sparse matrix as a dense array (for visualization only, as it defeats the purpose of sparsity)
print(interaction_matrix.toarray())
