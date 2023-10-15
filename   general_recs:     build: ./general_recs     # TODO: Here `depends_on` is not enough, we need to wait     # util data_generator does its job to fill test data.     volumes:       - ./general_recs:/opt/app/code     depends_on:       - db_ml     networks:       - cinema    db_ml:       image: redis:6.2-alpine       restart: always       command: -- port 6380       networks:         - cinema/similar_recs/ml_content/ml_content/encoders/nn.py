import torch
import torch.nn as nn


class MLP(nn.Module):
    def __init__(
        self,
        input_dim,
        output_dim,
        hidden_units=(64, 64),
        hidden_activation=nn.ReLU(),
        output_activation=nn.Identity(),
    ):
        super().__init__()

        layers = []
        units = input_dim
        for next_units in hidden_units:
            layers.append(nn.Linear(units, next_units))
            layers.append(hidden_activation)
            units = next_units
        layers.append(nn.Linear(units, output_dim))
        layers.append(output_activation)

        self.nn = nn.Sequential(*layers)  # .apply(initialize_weight)

    def forward(self, x):
        return self.nn(x)
