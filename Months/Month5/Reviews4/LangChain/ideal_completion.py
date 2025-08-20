# ideal_completion.py

from langchain_chroma import Chroma

def get_docs(collection_name, persist_directory, embeddings, query, k):
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

    return vector_store.similarity_search(query, k=k)