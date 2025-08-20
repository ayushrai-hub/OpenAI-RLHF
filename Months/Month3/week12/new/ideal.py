import numpy as np
import torch
def select_samples(model, unlabeled_data, strategy='uncertainty', num_samples=10):
    """
    Select insightful examples and return their indices and labels.

    Args:
        model (torch.nn.Module): Model applied for picking examples.
        unlabeled_data (DataLoader): DataLoader for unlabelled data set.
        strategy (str): Scheme for example selection ('uncertainty', 'entropy', 'random').
        num_samples (int): Amount of examples to pick.

    Returns:
        selected_indices (list): Indices of chosen examples.
        selected_labels (list): Labels corresponding to chosen examples.
    """
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    scores = []
    indices = []
    labels = []

    with torch.no_grad():
        for idx, (images, true_labels) in enumerate(unlabeled_data):
            images = images.to(device)
            outputs = model(images)  # Acquire raw logits
            probabilities = torch.softmax(outputs, dim=1)  # Convert logits to probabilities

            if strategy == 'uncertainty':
                uncertainty_scores = 1 - torch.max(probabilities, dim=1).values
                scores.extend(uncertainty_scores.cpu().numpy())
                indices.extend([idx] * len(images))
                labels.extend(true_labels.numpy())

            elif strategy == 'entropy':
                entropy_scores = -torch.sum(probabilities * torch.log(probabilities + 1e-10), dim=1)
                scores.extend(entropy_scores.cpu().numpy())
                indices.extend([idx] * len(images))
                labels.extend(true_labels.numpy())

            elif strategy == 'random':
                indices.extend([idx] * len(images))
                labels.extend(true_labels.numpy())

    if strategy in ['uncertainty', 'entropy']:
        scores = np.array(scores)
        indices = np.array(indices)
        labels = np.array(labels)
        sorted_indices = np.argsort(scores)[::-1]
        selected = sorted_indices[:num_samples]
        selected_indices = indices[selected]
        selected_labels = labels[selected]
    else:
        selected = np.random.choice(range(len(indices)), size=num_samples, replace=False)
        selected_indices = [indices[i] for i in selected]
        selected_labels = [labels[i] for i in selected]

    return selected_indices.tolist(), selected_labels.tolist()
def active_learning_cycle(model, train_loader, val_loader, test_loader, unlabeled_data, method, iterations=5,
                          samples_per_iteration=2):
    """
    Primary loop for Active Learning.
    
    Args:
        model (torch.nn.Module): Model for training.
        train_loader (DataLoader): Loader for training data.
        val_loader (DataLoader): Loader for validation data.
        test_loader (DataLoader): Loader for test data.
        unlabeled_data (DataLoader): Loader for unlabelled data.
        method (str): Active learning strategy.
        iterations (int): Number of Active Learning loops.
        samples_per_iteration (int): Samples chosen per iteration.
    
    Returns:
        model (torch.nn.Module): Refined model following Active Learning.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    for i in range(iterations):
        print(f"Active Learning Cycle {i + 1}/{iterations}")

        # Training using current labeled data
        train_model(model, train_loader, val_loader, epochs=2)

        # Pick new examples for labeling
        selected_indices, selected_labels = select_samples(model, unlabeled_data, strategy=method, num_samples=samples_per_iteration)

        # Display chosen indices
        print(f"Samples chosen for labeling: {selected_indices}")

        # Refresh training data with new labeled examples
        new_data = []
        for idx in selected_indices:
            images, _ = unlabeled_data.dataset[idx]
            new_data.append((images.numpy(), selected_labels.pop(0)))

        # Compose new dataset and dataloader by combining old training data with new data
        train_dataset_full = torch.utils.data.ConcatDataset([train_loader.dataset, new_data])
        train_loader = torch.utils.data.DataLoader(train_dataset_full, batch_size=train_loader.batch_size, shuffle=True)

        # Assess the model
        evaluate_model(model, test_loader)

    return model
