def log_epoch(logger, epochs, losses, accuracies):
    total_epochs = len(epochs)
    for epoch in range(total_epochs):
        logger.info(f"Epoch {epochs[epoch]}/{total_epochs} | Loss: {losses[epoch]} | Accuracy: {accuracies[epoch]}")
