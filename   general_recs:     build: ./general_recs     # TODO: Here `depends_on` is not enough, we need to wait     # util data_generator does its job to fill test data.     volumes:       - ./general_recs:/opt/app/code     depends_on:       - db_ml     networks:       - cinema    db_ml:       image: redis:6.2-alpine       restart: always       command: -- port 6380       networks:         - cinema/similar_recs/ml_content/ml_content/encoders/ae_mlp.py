import numpy.typing as npt
import torch


class AE(torch.nn.Module):
    """Basic autoencoder."""

    def __init__(self, input_dim: int):
        super().__init__()

        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 16),
            torch.nn.Sigmoid(),
        )

        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(16, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, input_dim),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def encode(self, x: npt.ArrayLike) -> npt.ArrayLike:
        x_t = torch.tensor(x, dtype=torch.float32)
        return self.encoder(x_t).detach().numpy()

    def save_encoder(self, path: str) -> None:
        torch.save(self.encoder.state_dict(), path)

    def load_encoder(self, path: str) -> None:
        self.encoder.load_state_dict(torch.load(path))

    @property
    def emb_size(self) -> int:
        return 16
