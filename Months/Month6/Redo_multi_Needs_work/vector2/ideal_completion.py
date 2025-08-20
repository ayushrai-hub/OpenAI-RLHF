import numpy as np

def search_by_batch_centroid(vector_database: np.ndarray, batch_vectors: np.ndarray) -> np.ndarray:
    """
    Finds the top 5 most similar items from the database for each query vector using batch centroid search.

    Args:
        vector_database (np.ndarray): Database vectors of shape (num_items, 20, 128).
        batch_vectors (np.ndarray): Batch of query vectors of shape (32, 128).

    Returns:
        np.ndarray: Array of shape (32, 5) containing indices of the top 5 most similar items.
                    If there are fewer than 5 items in the database, the remaining entries are filled with -1.
                    If the database is empty, returns an array filled with -1s.
    """
    num_items = vector_database.shape[0]
    batch_size = batch_vectors.shape[0]
    top_k = 5

    if num_items == 0:
        return -np.ones((batch_size, top_k), dtype=int)

    # Compute centroids for each item (mean over 20 vectors per item)
    centroids = np.mean(vector_database, axis=1)  # Shape: (num_items, 128)

    # Normalize centroids to unit vectors
    centroid_norms = np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-10
    normalized_centroids = centroids / centroid_norms  # Shape: (num_items, 128)

    # Normalize batch query vectors
    batch_norms = np.linalg.norm(batch_vectors, axis=1, keepdims=True) + 1e-10
    normalized_batch = batch_vectors / batch_norms  # Shape: (batch_size, 128)

    # Compute cosine similarity between batch queries and centroids
    similarity_scores = np.dot(normalized_batch, normalized_centroids.T)  # Shape: (batch_size, num_items)

    # Determine actual top_k based on the number of available items
    actual_top_k = min(top_k, num_items)

    # Get indices of top actual_top_k items for each query
    top_indices = np.argsort(-similarity_scores, axis=1)[:, :actual_top_k]  # Shape: (batch_size, actual_top_k)

    # Pad with -1 if the number of items is less than top_k
    if actual_top_k < top_k:
        padding = -np.ones((batch_size, top_k - actual_top_k), dtype=int)
        top_indices = np.hstack((top_indices, padding))  # Shape: (batch_size, top_k)

    return top_indices

def search_pairwise(vector_database: np.ndarray, batch_vectors: np.ndarray) -> np.ndarray:
    """
    Finds the top 5 most similar items from the database for each query vector using pairwise search.

    Args:
        vector_database (np.ndarray): Database vectors of shape (num_items, 20, 128).
        batch_vectors (np.ndarray): Batch of query vectors of shape (32, 128).

    Returns:
        np.ndarray: Array of shape (32, k) where k is min(5, num_items), containing indices of the top k most similar items.
                    If the database is empty, returns an empty array with shape (32, 0).
    """
    num_items = vector_database.shape[0]
    batch_size = batch_vectors.shape[0]
    top_k = 5

    if num_items == 0:
        return np.array([], dtype=int).reshape(batch_size, 0)

    # Reshape the database to combine items and their 20 vectors: (num_items * 20, 128)
    flattened_database = vector_database.reshape(num_items * 20, 128)

    # Normalize database vectors
    db_norms = np.linalg.norm(flattened_database, axis=1, keepdims=True) + 1e-10
    normalized_db = flattened_database / db_norms  # Shape: (num_items * 20, 128)

    # Normalize batch query vectors
    batch_norms = np.linalg.norm(batch_vectors, axis=1, keepdims=True) + 1e-10
    normalized_batch = batch_vectors / batch_norms  # Shape: (batch_size, 128)

    # Compute cosine similarity between batch queries and all database vectors
    similarity_scores = np.dot(normalized_batch, normalized_db.T)  # Shape: (batch_size, num_items * 20)

    # Reshape similarity scores to (batch_size, num_items, 20)
    similarity_scores_reshaped = similarity_scores.reshape(batch_size, num_items, 20)

    # For each query and item, get the maximum similarity across the item's 20 vectors
    max_similarity_per_item = np.max(similarity_scores_reshaped, axis=2)  # Shape: (batch_size, num_items)

    # Determine actual top_k based on the number of available items
    actual_top_k = min(top_k, num_items)

    # Get indices of top actual_top_k items for each query
    top_indices = np.argsort(-max_similarity_per_item, axis=1)[:, :actual_top_k]  # Shape: (batch_size, actual_top_k)

    return top_indices

# Sample data for testing
np.random.seed(42)

# Define test parameters
num_items_list = [0, 3, 10]  # Testing edge cases: empty, fewer than top_k, and more than top_k items
num_views_per_item = 20
vector_dim = 128
batch_size = 32

for num_items in num_items_list:
    print(f"\nTesting with {num_items} items in the database:")

    # Generate a vector database with shape (num_items, 20, 128)
    vector_database = np.random.randn(num_items, num_views_per_item, vector_dim)

    # Generate batch query vectors with shape (32, 128)
    batch_vectors = np.random.randn(batch_size, vector_dim)

    # Perform batch centroid search and pairwise search
    batch_centroid_results = search_by_batch_centroid(vector_database, batch_vectors)
    pairwise_results = search_pairwise(vector_database, batch_vectors)

    print("Batch Centroid Search Results:")
    print(batch_centroid_results)
    print("Shape:", batch_centroid_results.shape)

    print("\nPairwise Search Results:")
    print(pairwise_results)
    print("Shape:", pairwise_results.shape)
