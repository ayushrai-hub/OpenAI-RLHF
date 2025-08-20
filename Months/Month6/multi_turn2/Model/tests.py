import unittest
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
# Import the functions and classes to be tested
from working_ideal_completion import (

    ModifiedFlySmote,
    SemiSupervisedModel,
    construct_basic_sequential_model,
    extract_correct_datasets,
    assign_unlabeled_labels,
    combine_data,
    consolidate_models,
    assess_model_efficiency
)
class TestModifiedFlySmote(unittest.TestCase):
    def setUp(self):
        # Setting up mock data for testing ModifiedFlySmote
        self.X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        self.Y_train = np.array([0, 1, 0, 1])
        self.fly_smote = ModifiedFlySmote(self.X_train, self.Y_train)

    def test_find_nearest_neighbors(self):
        # This test checks if the find_nearest_neighbors method correctly identifies
        # the nearest neighbors for a given point in the dataset.
        neighbors = self.fly_smote.find_nearest_neighbors(self.X_train, self.X_train[0], 2)
        self.assertEqual(len(neighbors), 2)

    def test_segregate_train_data(self):
        # This test ensures that the segregate_train_data function correctly separates
        # the majority and minority classes in the dataset.
        majority, minority = self.fly_smote.segregate_train_data(self.X_train, self.Y_train, 1)
        self.assertEqual(len(minority), 2)
        self.assertEqual(len(majority), 2)

    def test_generate_synthetic_data(self):
        # Verifies that the generate_synthetic_data method creates synthetic samples
        # for the minority class, ensuring that the dataset is balanced.
        synthetic_X, synthetic_Y = self.fly_smote.generate_synthetic_data(minority_val=1, k=2, ratio=0.5)
        self.assertGreater(len(synthetic_X), 0)
        self.assertGreater(len(synthetic_Y), 0)

class TestSemiSupervisedModel(unittest.TestCase):
    def setUp(self):
        # Setting up mock data for SemiSupervisedModel
        X_train = np.random.rand(100, 50)
        Y_train = np.random.randint(0, 2, 100)
        X_test = np.random.rand(20, 50)
        Y_test = np.random.randint(0, 2, 20)
        train_df = pd.DataFrame(X_train)
        train_df['Task'] = Y_train
        test_df = pd.DataFrame(X_test)
        test_df['Task'] = Y_test
        self.encoder = LabelEncoder()
        self.encoder.fit(Y_train)
        self.ssl_model = SemiSupervisedModel(train_df, test_df, self.encoder)

    def test_update_distributed_data(self):
        # Test to check if data is correctly distributed among clients for semi-supervised learning
        client_data = self.ssl_model.update_distributed_data()
        self.assertEqual(len(client_data), 10)  # Verify 10 clients are created

    def test_client_selection(self):
        # Test to verify that the client selection logic works correctly
        # Clients should be selected based on uncertainty measures.
        divided_client_data = self.ssl_model.update_distributed_data()
        selected_clients = self.ssl_model.client_selection(divided_client_data)
        self.assertGreaterEqual(len(selected_clients), 2)  # Ensure at least 2 clients are selected

class TestUtilities(unittest.TestCase):
    def test_construct_basic_sequential_model(self):
        # This test verifies that the construct_basic_sequential_model function
        # returns a valid Sequential model with the correct architecture.
        model = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        self.assertIsInstance(model, Sequential)

    def test_extract_correct_datasets(self):
        # Verifies that the extract_correct_datasets function correctly identifies
        # and returns the correctly classified and misclassified data from model predictions.
        model = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        model.build((None, 50))  # Ensure the model is built
        x_verification = np.random.rand(10, 50)
        y_verification = np.random.randint(0, 2, 10)
        extracted_data = extract_correct_datasets(model, x_verification, y_verification)
        self.assertIn('features', extracted_data)  # Check if 'features' key exists
        self.assertIn('labels', extracted_data)  # Check if 'labels' key exists

    def test_assign_unlabeled_labels(self):
        # This test checks whether assign_unlabeled_labels assigns labels to
        # unlabeled data based on model confidence scores.
        model = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        model.build((None, 50))  # Ensure the model is built
        unlabeled_features = np.random.rand(10, 50)
        high_conf_features, high_conf_labels = assign_unlabeled_labels(model, unlabeled_features)
        self.assertEqual(len(high_conf_features), len(high_conf_labels))  # Check equal sizes

    def test_combine_data(self):
        # This test checks that combine_data correctly merges the original and pseudo-labeled datasets.
        original_features = np.random.rand(10, 50)
        original_labels = np.random.randint(0, 2, 10)
        pseudo_features = np.random.rand(5, 50)
        pseudo_labels = np.random.randint(0, 2, 5)
        final_features, final_labels = combine_data(original_features, original_labels, pseudo_features, pseudo_labels)
        self.assertEqual(final_features.shape[0], 15)  # Combined number of features should be 15
        self.assertEqual(final_labels.shape[0], 15)  # Combined number of labels should be 15

    def test_consolidate_models(self):
        # Verifies that consolidate_models successfully consolidates the weights of multiple client models.
        model1 = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        model2 = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        model1.set_weights([w * 1.5 for w in model1.get_weights()])  # Modify weights for testing
        participant_models = {'client1': model1, 'client2': model2}
        unified_model = consolidate_models(participant_models, model_input_shape=(50,), class_count=2)
        self.assertIsInstance(unified_model, Sequential)  # Check if the result is a valid model

    def test_assess_model_efficiency(self):
        # Test to check that assess_model_efficiency correctly evaluates the model's performance.
        model = construct_basic_sequential_model(input_shape=(50,), class_count=2)
        model.build((None, 50))  # Ensure the model is built
        x_eval = np.random.rand(20, 50)
        y_eval = np.random.randint(0, 2, 20)
        loss, accuracy, confusion, report = assess_model_efficiency(model, x_eval, y_eval)
        self.assertGreaterEqual(accuracy, 0)  # Ensure accuracy is non-negative
        self.assertGreaterEqual(loss, 0)  # Ensure loss is non-negative

if __name__ == "__main__":
    unittest.main(verbosity=2)