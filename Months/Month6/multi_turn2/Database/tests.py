from ideal_completion import search_pairwise, search_by_batch_centroid
import unittest
import numpy as np


class TestGradientDescent(unittest.TestCase):
    def test_centroid_similarity_db_greater_than_five(self):
        # Test if top 5 classes are returned if the vector db contains more than 5 vectors
        # This is an important test case because it verifies that the index correctly returns top 5 most similar
        # classes when a centroid matching method is used
        vector_db = np.random.uniform(low=0, high=1, size=(25600, 400, 128))
        batch_vectors = np.random.uniform(low=0, high=1, size=(512, 128))
        top_5 = search_by_batch_centroid(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 5)

        # Check if all top classes are valid
        self.assertTrue(all([num > 0 for num in top_5]))

    def test_centroid_similarity_db_less_than_five(self):
        # Test if top 5 classes are returned if the vector db contains less than 5 vectors
        # This is an important test case because it verifies that the index correctly returns top most similar
        # classes when a centroid matching method is used
        vector_db = np.random.uniform(low=0, high=1, size=(2, 400, 128))
        batch_vectors = np.random.uniform(low=0, high=1, size=(512, 128))
        top_5 = search_by_batch_centroid(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 5)

        # Check if all top classes are valid
        self.assertTrue(all([num == -1 for num in top_5[2:]]))

    def test_centroid_similarity_db_empty(self):
        # Test if list containing only -1 is returned (which is the expected behavior) when the index is empty 
        # This is an important test case because it verifies that the index code does not break when the
        # index is empty
        vector_db = np.random.uniform(low=0, high=1, size=(0, 400, 128))
        batch_vectors = np.random.uniform(low=0, high=1, size=(512, 128))
        top_5 = search_by_batch_centroid(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 5)

        # Check if all top classes are valid
        self.assertTrue(all([num == -1 for num in top_5]))

    def test_pairwise_similarity_db_greater_than_five(self):
        # Test if top 5 classes are returned if the vector db contains more than 5 vectors
        np.random.seed(0)
        vector_db = np.random.uniform(low=0, high=1, size=(25600, 400, 128))
        batch_vectors = np.random.power(5, (512, 128))
        top_5 = search_pairwise(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 5)
        
        # Check if all top classes are valid indices
        self.assertTrue(all([0 <= num < 25600 for num in top_5]))


    def test_pairwise_similarity_db_less_than_five(self):
        # Test if top 5 classes are returned if the vector db contains less than 5 vectors
        # This is an important test case because it verifies that the index correctly returns top most similar
        # classes when we use pairwise similarity
        
        # seeding for reproducible results
        np.random.seed(1)
        vector_db = np.random.uniform(low=0, high=1, size=(3, 400, 128))
        batch_vectors = np.random.power(5, (512, 128))
        top_5 = search_pairwise(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 3)
        self.assertEqual([1, 0, 2], list(top_5))
        # Check if all top classes are valid
        self.assertTrue(all([num >= 0 for num in top_5]))

    def test_pairwise_similarity_db_empty(self):
        # Test if empty array returned if the vector db is empty
        # This is an important test case because it verifies that the index correctly returns empty list
        # when we use pairwise similarity 
        np.random.seed(1)
        vector_db = np.random.uniform(low=0, high=1, size=(0, 400, 128))
        batch_vectors = np.random.power(5, (512, 128))
        top_5 = search_pairwise(vector_database=vector_db, batch_vectors=batch_vectors)
        self.assertEqual(len(top_5), 0)
        self.assertEqual([], list(top_5))


if __name__ == '__main__':
    unittest.main(verbosity=2)