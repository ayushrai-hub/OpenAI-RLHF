import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import classification_report, confusion_matrix

# Specifying tri_class_ranges
tri_class_ranges = {
    '0-8h': (0, 480),
    '8-40h': (480.01, 2400),
    '40+h': (2400.01, float('inf')),
}

# Function for categorizing completion duration as per tri_class_ranges
def classify_duration(duration):
    for category, (low, high) in tri_class_ranges.items():
        if low <= duration <= high:
            return category
    return 'Unknown'

# Class for Model Evaluation
class EvaluateModel:
    def __init__(self, actual_categorization, predicted_categorization, labels):
        self.actual_cats = actual_categorization
        self.predicted_cats = predicted_categorization
        self.labels = labels
    
    def run_evaluation(self):
        cls_report = classification_report(self.actual_cats, self.predicted_cats, labels=self.labels, output_dict=True)
        confusion_mat = confusion_matrix(self.actual_cats, self.predicted_cats, labels=self.labels)
        return cls_report, confusion_mat

if __name__ == '__main__':
    # Generating demonstration mock data 
    np.random.seed(42)
    samples_count = 100
    embed_dimension = 10

    # Creating random embeddings and completion durations between 1 minute to 5000 minutes
    embeds = np.random.rand(samples_count, embed_dimension)
    case_completion_times = np.random.randint(1, 5000, size=samples_count)

    # Formulating a DataFrame
    data_frame = pd.DataFrame({
        'embedding': list(embeds),
        'completion_time': case_completion_times
    })

    # Adding 'tri_class_target' column to DataFrame
    data_frame['tri_class_target'] = data_frame['completion_time'].apply(classify_duration)

    # Dividing the data into training and testing datasets
    data_frame_train, data_frame_test = train_test_split(data_frame, test_size=0.3, random_state=42)

    # Extracting embeddings and completion durations
    train_embed = np.stack(data_frame_train['embedding'].values)
    test_embed = np.stack(data_frame_test['embedding'].values)
    train_duration = data_frame_train['completion_time'].values
    test_duration = data_frame_test['completion_time'].values
    train_categories = data_frame_train['tri_class_target'].values
    test_categories = data_frame_test['tri_class_target'].values

    # Processing each testing scenario
    test_predictions = []
    for emb in test_embed:
        # Calculating cosine similarity with training embeddings
        similar_scores = cosine_similarity([emb], train_embed)[0]
        # Identifying indices with similarity >= 0.85
        indices_similar = np.where(similar_scores >= 0.85)[0]
        if len(indices_similar) == 0:
            # No cases found similar
            test_predictions.append("No Similar Cases Found")
        else:
            # Getting the top 5 most similar cases
            significant_indices = indices_similar[np.argsort(similar_scores[indices_similar])[::-1][:5]]
            # Calculating mean completion duration
            avg_duration = np.mean(train_duration[significant_indices])
            test_predictions.append(avg_duration)

    # Categorizing actual completion durations
    actual_categorized = test_categories

    # Categorizing predicted completion durations
    predicted_categorized = []
    for prediction in test_predictions:
        if prediction == "No Similar Cases Found":
            predicted_categorized.append('Unknown')
        else:
            predicted_categorized.append(classify_duration(prediction))

    # Defining labels
    labels = list(tri_class_ranges.keys()) + ['Unknown']

    # Instantiating and executing evaluation
    model_evaluator = EvaluateModel(actual_categorized, predicted_categorized, labels)
    classification_report, confusion_matrix = model_evaluator.run_evaluation()
