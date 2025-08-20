import pandas as pd
def items_to_distributed_sublists(items_to_distribute: pd.Series, num_collections: int) -> list[pd.Series]:
    # Sort the series in descending order to allocate larger elements first
    # sorted_elements = sorted(elements_list, reverse=True)
    arranged_items = items_to_distribute.sort_values(ascending=False)

    # Create empty sublists
    collection_indices = [[] for _ in range(num_collections)]

    # Allocate the items by continually adding the next item to the sublist with the lowest total
    for idx, _ in arranged_items.items():
        smallest_collection = min(collection_indices, key=lambda x: items_to_distribute.iloc[x].sum())
        smallest_collection.append(idx)

    # Transform the indices into the actual series
    collections = [items_to_distribute.iloc[indices] for indices in collection_indices]

    assert sum(len(x) for x in collections) == len(items_to_distribute)
    assert len(collections) <= num_collections

    return collections