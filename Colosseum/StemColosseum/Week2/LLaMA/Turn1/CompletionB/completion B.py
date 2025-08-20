import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Sample text data
sample_text = "This is a simple example of a language model. It is not a full implementation of LLaMA."

# Preprocessing: Create a vocabulary and map characters to indices
chars = sorted(list(set(sample_text)))
vocab_size = len(chars)
char_to_idx = {char: idx for idx, char in enumerate(chars)}
idx_to_char = {idx: char for idx, char in enumerate(chars)}

# Hyperparameters
embedding_dim = 64
hidden_dim = 128
sequence_length = 10
batch_size = 16
num_epochs = 100
learning_rate = 0.001

# Dataset
class TextDataset(Dataset):
    def __init__(self, text, char_to_idx, sequence_length):
        self.text = text
        self.char_to_idx = char_to_idx
        self.sequence_length = sequence_length
        self.data = self.prepare_data()

    def prepare_data(self):
        sequences = []
        for i in range(len(self.text) - self.sequence_length):
            seq = self.text[i:i + self.sequence_length]
            target = self.text[i + self.sequence_length]
            sequences.append((seq, target))
        return sequences

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq, target = self.data[idx]
        seq_idx = torch.tensor([self.char_to_idx[char] for char in seq], dtype=torch.long)
        target_idx = torch.tensor(self.char_to_idx[target], dtype=torch.long)
        return seq_idx, target_idx

dataset = TextDataset(sample_text, char_to_idx, sequence_length)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Model
class SimpleLLaMA(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(SimpleLLaMA, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = self.fc(x[:, -1, :])
        return x

model = SimpleLLaMA(vocab_size, embedding_dim, hidden_dim)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training
model.train()
for epoch in range(num_epochs):
    total_loss = 0
    for seq, target in dataloader:
        optimizer.zero_grad()
        output = model(seq)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f'Epoch {epoch+1}/{num_epochs}, Loss: {total_loss/len(dataloader)}')

# Text generation
def generate_text(model, start_seq, char_to_idx, idx_to_char, length=100):
    model.eval()
    input_seq = torch.tensor([char_to_idx[char] for char in start_seq], dtype=torch.long).unsqueeze(0)
    generated_text = start_seq
    for _ in range(length):
        with torch.no_grad():
            output = model(input_seq)
            _, predicted_idx = torch.max(output, dim=1)
            predicted_char = idx_to_char[predicted_idx.item()]
            generated_text += predicted_char
            # Prepare the new input sequence by appending the predicted character
            predicted_idx = predicted_idx.unsqueeze(0)  # Add batch dimension
            new_input = torch.cat((input_seq[:, 1:], predicted_idx), dim=1)
            input_seq = new_input
    return generated_text

start_sequence = "This is a "
generated_text = generate_text(model, start_sequence, char_to_idx, idx_to_char)
print(f'Generated Text: {generated_text}')
