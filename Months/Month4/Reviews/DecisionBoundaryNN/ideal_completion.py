# ideal_completion.py

import torch
import torch.nn as nn

class DecisionBoundaryNN(nn.Module):
    def __init__(self):
        super(DecisionBoundaryNN, self).__init__()
        self.layer1 = nn.Linear(2, 2)  # Input dimension (x, y), two neurons
        self.layer2 = nn.Linear(2, 1)  # Input from hidden layer to one neuron output
        self.sigmoid = nn.Sigmoid()

        # Setting weights and biases manually
        with torch.no_grad():
            # First neuron: f1 = σ(10y)  # For y > 0
            self.layer1.weight[0] = torch.tensor([0.0, 100.0])
            self.layer1.bias[0] = torch.tensor(0.0)
            
            # Second neuron: f2 = σ(10(-y + 2x + 3))  # For y < 2x + 3
            self.layer1.weight[1] = torch.tensor([200.0, -100.0])
            self.layer1.bias[1] = torch.tensor(300.0)

            # Output neuron: combine both conditions with AND
            self.layer2.weight[0] = torch.tensor([100.0, 100.0])
            self.layer2.bias[0] = torch.tensor(-150.0)  # High bias for AND operation


    def forward(self, x):
        # First layer forward pass
        out1 = self.sigmoid(self.layer1(x))
        # Second layer forward pass
        out2 = self.sigmoid(self.layer2(out1))
        return out2