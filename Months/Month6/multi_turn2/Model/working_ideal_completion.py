import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.metrics import confusion_matrix, classification_report

class ModifiedFlySmote:
    def __init__(self, X_train, Y_train):
        self.X_train = X_train
        self.Y_train = Y_train

    def find_nearest_neighbors(self, data, sample_point, k):
        """Find k nearest neighbors for a given sample point."""
        if len(data) <= k:
            return np.arange(len(data))
        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(data)
        distances, indices = nbrs.kneighbors([sample_point])
        return indices[0][1:]  # Exclude the point itself

    def segregate_train_data(self, X, y, minority_val):
        """Separate data into majority and minority classes."""
        minority_indices = np.where(y == minority_val)[0]
        majority_indices = np.where(y != minority_val)[0]
        return X[majority_indices], X[minority_indices]

    def generate_synthetic_data(self, minority_val=1, k=5, ratio=1.0):
        """Generate synthetic samples for minority class using SMOTE-like approach."""
        majority_data, minority_data = self.segregate_train_data(self.X_train, self.Y_train, minority_val)
        
        if len(minority_data) == 0:
            # Handle case where there's no minority data
            return np.array([[0] * self.X_train.shape[1]]), np.array([minority_val])
        
        synthetic_samples = []
        # Ensure at least one synthetic sample is generated
        n_synthetic = max(1, int((len(majority_data) - len(minority_data)) * ratio))
        
        for _ in range(n_synthetic):
            idx = np.random.randint(0, len(minority_data))
            sample = minority_data[idx]
            k_adjusted = min(k, len(minority_data) - 1)  # Adjust k if not enough samples
            if k_adjusted > 0:
                neighbors = self.find_nearest_neighbors(minority_data, sample, k_adjusted)
                neighbor_idx = np.random.choice(neighbors)
                neighbor = minority_data[neighbor_idx]
                alpha = np.random.random()
                synthetic_sample = sample + alpha * (neighbor - sample)
                synthetic_samples.append(synthetic_sample)
            else:
                # If no neighbors available, just use the sample itself with small random noise
                noise = np.random.normal(0, 0.01, size=sample.shape)
                synthetic_samples.append(sample + noise)
        
        synthetic_X = np.array(synthetic_samples)
        synthetic_Y = np.full(len(synthetic_samples), minority_val)
        
        return synthetic_X, synthetic_Y

class SemiSupervisedModel:
    def __init__(self, train_df, test_df, label_encoder, n_clients=10):
        self.train_df = train_df
        self.test_df = test_df
        self.label_encoder = label_encoder
        self.n_clients = n_clients
        self.model = None

    def update_distributed_data(self):
        """Distribute data among clients."""
        n_samples = len(self.train_df)
        samples_per_client = max(1, n_samples // self.n_clients)
        client_data = {}
        
        for i in range(self.n_clients):
            start_idx = i * samples_per_client
            end_idx = start_idx + samples_per_client if i < self.n_clients - 1 else n_samples
            client_data[f'client_{i}'] = self.train_df.iloc[start_idx:end_idx].copy()
        
        return client_data

    def client_selection(self, divided_client_data, selection_ratio=0.3):
        """Select clients based on data uncertainty."""
        uncertainties = {}
        for client_id, data in divided_client_data.items():
            if len(data) > 0:
                # Calculate uncertainty based on class distribution
                class_dist = data['Task'].value_counts(normalize=True)
                uniform_dist = np.ones(len(class_dist)) / len(class_dist)
                uncertainties[client_id] = compute_sym_uncert(class_dist.values, uniform_dist)
        
        # Select clients with highest uncertainty
        n_select = max(2, int(self.n_clients * selection_ratio))
        selected_clients = sorted(uncertainties.keys(), 
                                key=lambda x: uncertainties[x], 
                                reverse=True)[:n_select]
        return selected_clients

def compute_sym_uncert(p, q):
    """Compute symmetric uncertainty between two distributions."""
    eps = 1e-10
    p = np.array(p) + eps
    q = np.array(q) + eps
    
    p_norm = p / np.sum(p)
    q_norm = q / np.sum(q)
    
    kl_pq = np.sum(p_norm * np.log(p_norm / q_norm))
    kl_qp = np.sum(q_norm * np.log(q_norm / p_norm))
    
    sym_uncert = (kl_pq + kl_qp) / 2
    return min(sym_uncert, 1.0)  # Clip to [0,1]

def construct_basic_sequential_model(input_shape, class_count):
    """Construct a basic sequential neural network."""
    model = Sequential([
        Dense(128, activation='relu', input_shape=input_shape),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(class_count, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    return model

def extract_correct_datasets(model, x_verification, y_verification):
    """Extract correctly classified samples from the dataset."""
    predictions = model.predict(x_verification)
    predicted_classes = np.argmax(predictions, axis=1)
    correct_indices = predicted_classes == y_verification
    
    return {
        'features': x_verification[correct_indices],
        'labels': y_verification[correct_indices]
    }

def assign_unlabeled_labels(model, unlabeled_features, confidence_threshold=0.8):
    """Assign labels to unlabeled data based on model confidence."""
    predictions = model.predict(unlabeled_features)
    max_confidences = np.max(predictions, axis=1)
    high_conf_indices = max_confidences >= confidence_threshold
    
    high_conf_features = unlabeled_features[high_conf_indices]
    high_conf_labels = np.argmax(predictions[high_conf_indices], axis=1)
    
    return high_conf_features, high_conf_labels

def combine_data(original_features, original_labels, pseudo_features, pseudo_labels):
    """Combine original and pseudo-labeled datasets."""
    final_features = np.vstack([original_features, pseudo_features])
    final_labels = np.concatenate([original_labels, pseudo_labels])
    return final_features, final_labels

def consolidate_models(participant_models, model_input_shape, class_count):
    """Consolidate weights from multiple client models."""
   
    consolidated_model = construct_basic_sequential_model(model_input_shape, class_count)
    
    # Average the weights across all models
    avg_weights = []
    for i in range(len(consolidated_model.get_weights())):
        layer_weights = np.array([model.get_weights()[i] 
                                for model in participant_models.values()])
        avg_weights.append(np.mean(layer_weights, axis=0))
    
    consolidated_model.set_weights(avg_weights)
    return consolidated_model

def assess_model_efficiency(model, x_eval, y_eval):
    """Evaluate model performance."""
    loss, accuracy = model.evaluate(x_eval, y_eval, verbose=0)
    predictions = model.predict(x_eval)
    predicted_classes = np.argmax(predictions, axis=1)
    
    conf_matrix = confusion_matrix(y_eval, predicted_classes)
    class_report = classification_report(y_eval, predicted_classes)
    
    return loss, accuracy, conf_matrix, class_report