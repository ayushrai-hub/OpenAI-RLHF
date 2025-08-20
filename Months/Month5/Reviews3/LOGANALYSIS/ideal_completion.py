# ideal_completion.py

def log_epoch(logger, epochs, losses, accuracies):
    total_epochs = len(epochs)
    for epoch in range(total_epochs):
        logger.info(f"epoch {epochs[epoch]}/{total_epochs} | Loss: {losses[epoch]} | Accuracy: {accuracies[epoch]}")