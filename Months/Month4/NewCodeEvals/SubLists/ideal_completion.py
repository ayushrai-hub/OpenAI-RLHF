#ideal_completion.py
import pandas as pd

def items_to_distributed_sublists(items_to_distribute: pd.Series, num_collections: int) -> list[pd.Series]:
    # Sort the series in descending order to allocate larger elements first
    arranged_items = items_to_distribute.sort_values(ascending=False)

    # Create empty sublists
    collection_indices = [[] for _ in range(num_collections)]
    
    # Ensure that each collection gets at least one item (if there are enough items)
    arranged_items_iter = iter(arranged_items.index)
    for i in range(min(num_collections, len(arranged_items))):
        collection_indices[i].append(next(arranged_items_iter))
    
    # Allocate the remaining items by adding the next item to the sublist with the lowest total
    for idx in arranged_items_iter:
        smallest_collection = min(collection_indices, key=lambda x: items_to_distribute.iloc[x].sum())
        smallest_collection.append(idx)

    # Transform the indices into the actual series
    collections = [items_to_distribute.iloc[indices] for indices in collection_indices]

    # Ensure that the total number of items matches the original
    assert sum(len(x) for x in collections) == len(items_to_distribute)
    assert len(collections) <= num_collections

    return collections