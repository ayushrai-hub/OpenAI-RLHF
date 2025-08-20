from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
import unittest
import os
from ideal_completion import get_docs

class TestDataframeModification(unittest.TestCase):

    def setUp(self):
        def insert_data(embeddings, collection_name="movie_reviews", persist_directory="./chroma_db"):
            if os.path.exists(persist_directory):
                return
            from langchain_core.documents import Document

            review1 = Document("Movie1 is a great movie.")
            review2 = Document("Movie2 is a bad movie.")
            review3 = Document("Movie3 is a good movie.")
            review4 = Document("Movie4 is a bad movie.")
            review5 = Document("Movie5 is a good movie.")
            review6 = Document("Movie6 is a bad movie.")
            review7 = Document("Movie7 is a good movie.")

            movie_reviews = [review1, review2, review3, review4, review5, review6, review7]
            
            VectorstoreIndexCreator(
                vectorstore_cls=Chroma,
                embedding=embeddings,
                vectorstore_kwargs={
                    "collection_name": collection_name,
                    "persist_directory": persist_directory,
                },
            ).from_documents(movie_reviews)

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.collection_name="movie_reviews"
        self.persist_directory="./chroma_db"
        insert_data(self.embeddings, collection_name=self.collection_name, persist_directory=self.persist_directory)

    def test_query_docs(self):
        query = "How is Movie1"
        result = get_docs(self.collection_name, self.persist_directory, self.embeddings, query,4)
        self.assertIsNotNone(result)
    
    def test_query_docs_list(self):
        query = "How is Movie1"
        result = get_docs(self.collection_name, self.persist_directory, self.embeddings, query, 4)
        self.assertIsInstance(result, list)

    def test_non_empty_query_docs(self):
        query = "How is Movie1"
        result = get_docs(self.collection_name, self.persist_directory, self.embeddings, query, 4)
        self.assertTrue(len(result) > 0)

    def test_not_more_than_k_docs(self):
        query = "How is Movie1"
        result = get_docs(self.collection_name, self.persist_directory, self.embeddings, query, 4)
        self.assertTrue(len(result) <= 4)

if __name__ == '__main__':
    unittest.main()