import numpy as np
import faiss

def search_by_batch_centroid(vector_database: np.ndarray, batch_vectors: np.ndarray) -> np.ndarray:
    num_classes, num_vectors_per_class, vector_dim = vector_database.shape

    class_centroids = vector_database.mean(axis=1).astype(np.float32)
    batch_centroid = batch_vectors.mean(axis=0).reshape(1, -1).astype(np.float32)

    index = faiss.IndexFlatIP(vector_dim)

    faiss.normalize_L2(class_centroids)
    faiss.normalize_L2(batch_centroid)

    index.add(class_centroids)

    k = 5
    _, indices = index.search(batch_centroid, k)

    return indices[0].astype(int)

def search_pairwise(vector_database: np.ndarray, batch_vectors: np.ndarray) -> np.ndarray:
    num_classes, num_vectors_per_class, vector_dim = vector_database.shape

    if num_classes == 0 or num_vectors_per_class == 0:
        return np.array([], dtype=int)

    database_flat = vector_database.reshape(num_classes * num_vectors_per_class, vector_dim).astype(np.float32)

    index = faiss.IndexFlatIP(vector_dim)

    faiss.normalize_L2(database_flat)
    batch_vectors_normalized = batch_vectors.astype(np.float32)
    faiss.normalize_L2(batch_vectors_normalized)

    index.add(database_flat)

    k = 1
    _, indices = index.search(batch_vectors_normalized, k)

    class_indices = indices.flatten() // num_vectors_per_class

    freq_counts = np.bincount(class_indices, minlength=num_classes)
    class_idx_array = np.arange(num_classes)
    sorting_array = np.column_stack((freq_counts, class_idx_array))
    sorted_indices = sorting_array[np.lexsort((-sorting_array[:, 1], -sorting_array[:, 0]))]

    non_zero_freq_indices = sorted_indices[sorted_indices[:, 0] > 0][:, 1]

    if len(non_zero_freq_indices) == 0:
        return np.array([], dtype=int)
    elif len(non_zero_freq_indices) < 5:
        return non_zero_freq_indices.astype(int)
    else:
        return non_zero_freq_indices[:5].astype(int)
