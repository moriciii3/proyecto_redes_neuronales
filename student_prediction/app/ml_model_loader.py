import torch
import torch.nn as nn
from pathlib import Path

class StudentDropoutModel(nn.Module):
    def __init__(self, input_size, hidden_sizes, dropout_rates, activation='relu', num_classes=2):
        super().__init__()
        
        self.layers = nn.ModuleList()
        self.dropouts = nn.ModuleList()

        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'tanh':
            self.activation = nn.Tanh()

        prev = input_size
        for hs, dr in zip(hidden_sizes, dropout_rates):
            self.layers.append(nn.Linear(prev, hs))
            self.dropouts.append(nn.Dropout(dr))
            prev = hs

        self.output = nn.Linear(prev, num_classes)

    def forward(self, x):
        for layer, drop in zip(self.layers, self.dropouts):
            x = drop(self.activation(layer(x)))
        return self.output(x)

def load_model():
    model_path = Path(__file__).resolve().parents[2] / "student_model.pt"
    model = StudentDropoutModel(
        input_size=16,
        hidden_sizes=[128, 64, 32, 16],
        dropout_rates=[0.4, 0.3, 0.2, 0.1],
        activation="relu",
        num_classes=2
    )
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model
