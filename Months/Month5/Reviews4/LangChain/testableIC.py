from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings  # Assuming OpenAI embeddings

def get_docs(collection_name: str, persist_directory: str, embeddings: str, query: str, k: int) -> list:
    # Initialize the embedding function
    embeder = OpenAIEmbeddings(model=embeddings)  # Adjust if your embedding model is different

    # Initialize the Chroma vector store from the persisted directory
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_function=embeder.embed_query
    )

    # Perform a similarity search with the given query and return the results
    results = vectorstore.similarity_search(query, k=k)
    return results
