# Example Model Definition

"""
This is a placeholder model definition for the example project.
Replace with actual model architecture.
"""

import torch
import torch.nn as nn

class ExampleModel(nn.Module):
    """
    Simple example model for demonstration.
    """
    def __init__(self, input_dim=20, hidden_dim=64, output_dim=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.net(x)

if __name__ == "__main__":
    model = ExampleModel()
    print(f"Model parameters: {sum(p.numel() for p in model.parameters())}")
