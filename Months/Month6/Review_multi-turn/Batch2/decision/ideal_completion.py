import torch
import torch.nn as nn

class DecisionBoundaryNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden = nn.Linear(2, 2)
        self.output = nn.Linear(2, 1)
        # Manually initialize weights for the desired boundary
        with torch.no_grad():
            # Hidden layer for y > 0
            self.hidden.weight[0].zero_()
            self.hidden.weight[0,1] = 50.0
            self.hidden.bias[0] = 0.0
            # Hidden layer for y < 2x+3
            self.hidden.weight[1,0] = 20.0
            self.hidden.weight[1,1] = -10.0
            self.hidden.bias[1] = 30.0
            # Output layer to AND the conditions
            self.output.weight[0,0] = 50.0
            self.output.weight[0,1] = 50.0
            self.output.bias[0] = -75.0

    def forward(self, x):
        h = torch.sigmoid(self.hidden(x))
        out = torch.sigmoid(self.output(h))
        return out
