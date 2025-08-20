import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Flatten, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from scipy.stats import entropy


class ModifiedFlySmote:
    def __init__(self, X_train, Y_train):
        self.X_train = X_train
        self.Y_train = Y_train

    def find_nearest_neighbors(self, data, prediction, k):
        if len(data) < k:
            k = len(data)
        distances = []
        for index, element in enumerate(data):
            euclidean_distance = np.linalg.norm(np.array(element) - np.array(prediction))
            distances.append([euclidean_distance, index])

        neighbors = [item[1] for item in sorted(distances)[:k]]
        return neighbors

    def kSMOTE_balancing(self, majority, minority, k, ratio):
        S = []
        sample_count = int(ratio * (len(majority) - len(minority)))
        if k > 0:
            Nks = int(sample_count / k)
        else:
            Nks = sample_count
        random_minority_samples = random.sample(minority, min(k, len(minority)))
        for x_sample in random_minority_samples:
            nearest_neighbors = self.find_nearest_neighbors(minority, x_sample, k)
            synthetic_samples = []
            for _ in range(Nks):
                j = random.randint(0, len(nearest_neighbors) - 1)
                new_sample = ((minority[nearest_neighbors[j]] - x_sample) * random.random())
                synthetic_samples.append(x_sample + new_sample)
            S.append(synthetic_samples)
        return S

    def segregate_train_data(self, X_train, Y_train, minority_val):
        majority_class, minority_class = [], []
        for i in range(len(Y_train)):
            if Y_train[i] == minority_val:
                minority_class.append(X_train[i])
            else:
                majority_class.append(X_train[i])
        return majority_class, minority_class

    def generate_synthetic_data(self, minority_val, k, ratio):
        majority_class, minority_class = self.segregate_train_data(self.X_train, self.Y_train, minority_val)
        synthetic_x = self.kSMOTE_balancing(majority_class, minority_class, k, ratio)
        X_augmented, Y_augmented = [], []
        for cluster in synthetic_x:
            for sample in cluster:
                X_augmented.append(sample)
                Y_augmented.append(minority_val)
        X_augmented.extend(self.X_train)
        Y_augmented.extend(self.Y_train)
        return np.array(X_augmented), np.array(Y_augmented)


class SemiSupervisedModel:
    def __init__(self, train_set, test_set, encoder, clients_amount=10, iterations=5, epochs=10):
        self.train_set = train_set
        self.test_set = test_set
        self.encoder = encoder
        self.clients_amount = clients_amount
        self.iterations = iterations
        self.epochs = epochs
        self.collected_uncertainties = []

    def update_distributed_data(self):
        train_set = self.train_set.sample(frac=1).reset_index(drop=True)
        proportion_labeled = int(0.2 * len(train_set))
        labeled_section = train_set[:proportion_labeled]
        unlabeled_section = train_set[proportion_labeled:].drop('Task', axis=1)

        primary_client_share = 0.5
        secondary_client_share = 0.1
        heavy_clients = 2
        light_clients = self.clients_amount - heavy_clients

        data_size_primary_clients = int(primary_client_share * len(labeled_section) / heavy_clients)
        data_size_secondary_clients = int(secondary_client_share * len(labeled_section) / light_clients)

        major_unlabeled_share = 0.7
        minor_unlabeled_share = 0.05
        major_unlabeled_size = int(major_unlabeled_share * len(unlabeled_section) / heavy_clients)
        minor_unlabeled_size = int(minor_unlabeled_share * len(unlabeled_section) / light_clients)

        client_datasets = {
            f'client_{i+1}': {'train': pd.DataFrame(), 'validate': pd.DataFrame(), 'unlabeled': pd.DataFrame()}
            for i in range(self.clients_amount)
        }

        for i in range(self.clients_amount):
            identifier = f'client_{i+1}'
            if i < heavy_clients:
                start_index = i * data_size_primary_clients
                end_index = (i + 1) * data_size_primary_clients
                client_datasets[identifier]['train'] = labeled_section.iloc[start_index:end_index]
            else:
                start_index = heavy_clients * data_size_primary_clients + (i - heavy_clients) * data_size_secondary_clients
                end_index = start_index + data_size_secondary_clients
                client_datasets[identifier]['train'] = labeled_section.iloc[start_index:end_index]

        val_data_for_clients = labeled_section[int(0.1 * len(train_set)): int(0.2 * len(train_set))]
        validation_share_per_client = len(val_data_for_clients) // self.clients_amount
        for i in range(self.clients_amount):
            identifier = f'client_{i+1}'
            start_index = i * validation_share_per_client
            end_index = (i + 1) * validation_share_per_client
            client_datasets[identifier]['validate'] = val_data_for_clients.iloc[start_index:end_index]

        for i in range(self.clients_amount):
            identifier = f'client_{i+1}'
            if i < heavy_clients:
                start_index = i * major_unlabeled_size
                end_index = (i + 1) * major_unlabeled_size
            else:
                start_index = heavy_clients * major_unlabeled_size + (i - heavy_clients) * minor_unlabeled_size
                end_index = start_index + minor_unlabeled_size
            client_datasets[identifier]['unlabeled'] = unlabeled_section.iloc[start_index:end_index]

        return client_datasets

    def client_selection(self, participants, threshold=0.4):
        sym_uncertainty_values = []
        client_list = list(participants.keys())

        for client in client_list:
            client_data_x, client_data_y = zip(*participants[client]['train'].values)
            client_data_x = np.array(client_data_x).ravel()
            uncertainty = compute_sym_uncert(client_data_x, np.ones_like(client_data_x) / len(client_data_x))
            sym_uncertainty_values.append(uncertainty)

        self.collected_uncertainties.append(sym_uncertainty_values)
        threshold_uncertainty = np.quantile(sym_uncertainty_values, threshold)

        chosen_clients = [client for client, uncertainty in zip(client_list, sym_uncertainty_values) if uncertainty < threshold_uncertainty]

        return chosen_clients

    def execute(self):
        divided_client_data = self.update_distributed_data()
        model_input_def = (self.train_set.shape[1] - 1,)
        class_count = len(np.unique(self.train_set['Task']))

        unified_model = construct_basic_sequential_model(input_shape=model_input_def, class_count=class_count)

        for iteration_count in range(self.iterations):
            print(f"\nIteration {iteration_count + 1}/{self.iterations}")
            client_specific_models = {}
            selected_clients = self.client_selection(divided_client_data)

            for id in selected_clients:
                client_divisions = divided_client_data[id]
                x_train = client_divisions['train'].drop('Task', axis=1).values
                y_train = client_divisions['train']['Task'].values
                x_valid = client_divisions['validate'].drop('Task', axis=1).values
                y_valid = client_divisions['validate']['Task'].values
                x_unlab = client_divisions['unlabeled'].values

                minority_class = np.min(np.unique(y_train))
                modified_fly_smote = ModifiedFlySmote(x_train, y_train)
                equilibrated_x_train, equilibrated_y_train = modified_fly_smote.generate_synthetic_data(minority_class=minority_class, k=5, ratio=1.0)

                developed_model = construct_basic_sequential_model(input_shape=model_input_def, class_count=class_count)
                developed_model.set_weights(unified_model.get_weights())

                print(f"\nClient {id} - Developing basic model")
                developed_model.fit(equilibrated_x_train, equilibrated_y_train, epochs=self.epochs, validation_data=(x_valid, y_valid), verbose=0)

                print(f"\nClient {id} - Initial model evaluation")
                loss_val, accuracy_val, confusion, report_output = assess_model_efficiency(developed_model, x_valid, y_valid, self.encoder)
                print(f"Confusion Metrix:\n{confusion}")
                print(f"Report:\n{report_output}")

                correct_datasets = extract_correct_datasets(developed_model, x_valid, y_valid)
                refined_classifier = adjust_for_accurate_classifier(developed_model, model_input_def)
                refined_classifier.fit(correct_datasets['features'], correct_datasets['labels'], epochs=self.epochs, verbose=0)_per_round, verbose=0)

                print(f"\nClient {id} - Correct classifier assessment")
                loss_val, accuracy_val, confusion, report_output = assess_model_efficiency(refined_classifier, correct_datasets['features'], correct_datasets['labels'])
                print(f"Confusion Metrix:\n{confusion}")
                print(f"Report:\n{report_output}")

                assured_features, assured_labels = assign_unlabeled_labels(refined_classifier, x_unlab)
                x_train, y_train = combine_data(x_train, y_train, assured_features, assured_labels)

                developed_model.fit(x_train, y_train, epochs=self.epochs, verbose=0)
                client_specific_models[id] = developed_model

                print(f"\nClient {id} - Post-train model evaluation")
                loss_val, accuracy_val, confusion, report_output = assess_model_efficiency(developed_model, x_valid, y_valid, self.encoder)
                print(f"Confusion Metrix:\n{confusion}")
                print(f"Report:\n{report_output}")

            unified_model = consolidate_models(client_specific_models, model_input_def, class_count)

        x_eval = self.test_set.drop('Task', axis=1).values
        y_eval = self.test_set['Task'].values

        loss_val, accuracy_val, confusion, report_output = assess_model_efficiency(unified_model, x_eval, y_eval, self.encoder)
        return loss_val, accuracy_val, confusion, report_output


def construct_basic_sequential_model(input_shape, class_count):
    model = Sequential([
        Input(shape=input_shape),
        Flatten(),
        Dense(256, activation=None),
        BatchNormalization(),
        Dense(256, activation='relu'),
        Dropout(0.2),
        Dense(128, activation=None),
        BatchNormalization(),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(64, activation=None),
        BatchNormalization(),
        Dense(64, activation='relu'),
        Dropout(0.1),
        Dense(class_count, activation='softmax')
    ])
    model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def compute_sym_uncert(p, q):
    p = p / sum(p)
    q = q / sum(q)
    entropy_p = entropy(p)
    entropy_q = entropy(q)
    combined_entropy = entropy(p * q)
    sy_un = 2 * (entropy_p + entropy_q - combined_entropy) / (entropy_p + entropy_q)
    return sy_un


def adjust_for_accurate_classifier(basic_model, model_input_shape):
    dummy_input = np.zeros((1, *model_input_shape))
    basic_model(dummy_input)
    for layer in basic_model.layers[:2]:
        layer.trainable = False
    final_output = Dense(2, activation='softmax')(basic_model.layers[-4].output)
    adjusted_model = Model(inputs=basic_model.input, outputs=final_output)
    adjusted_model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return adjusted_model


def extract_correct_datasets(model, x_verification, y_verification):
    preds = model.predict(x_verification)
    predicted_vals = np.argmax(preds, axis=1)
    correct_idxs = np.where(predicted_vals == y_verification)[0]
    incorrect_idxs = np.where(predicted_vals != y_verification)[0]
    x_correct = x_verification[correct_idxs]
    y_correct = np.ones(len(correct_idxs))
    x_incorrect = x_verification[incorrect_idxs]
    y_incorrect = np.zeros(len(incorrect_idxs))
    accurate_features = np.concatenate((x_correct, x_incorrect), axis=0)
    accurate_labels = np.concatenate((y_correct, y_incorrect), axis=0)
    return {'features': accurate_features, 'labels': accurate_labels}


def assign_unlabeled_labels(model, unlabeled_features, conf_threshold=0.95):
    predict_probs = model.predict(unlabeled_features)
    max_probs = np.max(predict_probs, axis=1)
    predicted_vals = np.argmax(predict_probs, axis=1)
    above_threshold = max_probs > conf_threshold
    high_conf_features = unlabeled_features[above_threshold]
    high_conf_labels = predicted_vals[above_threshold]
    return high_conf_features, high_conf_labels


def combine_data(original_features, original_labels, pseudo_features, pseudo_labels):
    final_features = np.concatenate((original_features, pseudo_features), axis=0)
    final_labels = np.concatenate((original_labels, pseudo_labels), axis=0)
    return final_features, final_labels


def consolidate_models(participant_models, model_input_shape, class_count):
    unified_model = construct_basic_sequential_model(input_shape=model_input_shape, class_count=class_count)
    updated_weights = []
    for weights in zip(*[model.get_weights() for model in participant_models.values()]):
        updated_weights.append(np.mean(np.array(weights), axis=0))
    unified_model.set_weights(updated_weights)
    return unified_model


def assess_model_efficiency(unified_model, x_evaluation, y_encoded, encoder=None):
    test_loss, test_accuracy = unified_model.evaluate(x_evaluation, y_encoded, verbose=0)
    prediction_vectors = unified_model.predict(x_evaluation)
    expected_category = np.argmax(prediction_vectors, axis=1)
    confusion_metrix = confusion_matrix(y_encoded, expected_category)
    if encoder:
        classification_results = classification_report(y_encoded, expected_category, target_names=encoder.classes_)
    else:
        classification_results = classification_report(y_encoded, expected_category)
    return test_loss, test_accuracy, confusion_metrix, classification_results


# Load the dataset and preprocess
path_to_file = 'C:/Users/Anonymous_User/Dataset_Combined.csv'
dataframe = pd.read_csv(path_to_file)
output_encoder = LabelEncoder()
all_classifications = dataframe['Task'].dropna().unique()
output_encoder.fit(all_classifications)
sample_representative = dataframe.dropna().sample(n=1000)
X_rep = sample_representative.drop('Task', axis=1).values
y_rep = output_encoder.transform(sample_representative['Task'].values)
svd_model = TruncatedSVD(n_components=50)
X_rep_svd = svd_model.fit_transform(X_rep)
lda_analyzer = LinearDiscriminantAnalysis()
lda_analyzer.fit(X_rep_svd, y_rep)
X_main_data = dataframe.drop('Task', axis=1).values
X_main_svd = svd_model.transform(X_main_data)
X_main_lda = lda_analyzer.transform(X_main_svd)
y_main_data = output_encoder.transform(dataframe['Task'].values)
altered_data = pd.DataFrame(X_main_lda)
altered_data['Task'] = y_main_data
train_set, test_set = train_test_split(altered_data, test_size=0.1, random_state=42)

ssl_model = SemiSupervisedModel(train_set, test_set, output_encoder, clients_amount=10, iterations=5, epochs=10)
loss_val, accuracy_val, confusion, report_output = ssl_model.execute()
print(f"Test Loss: {loss_val}, Test Accuracy: {accuracy_val}")
print("Confusion Metrix:")
print(confusion)
print("Report:")
print(report_output)
