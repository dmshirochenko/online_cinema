import logging
import os
from abc import ABC, abstractmethod

from torch.utils.tensorboard import SummaryWriter


class AbstractLogger(ABC):
    @abstractmethod
    def log_scalar(self, tag: str, val: float, step: int):
        pass

    @abstractmethod
    def save_model(self, model, epoch: int):
        pass


class TBLogger(AbstractLogger):
    """Logging with tensorboard."""

    def __init__(self, log_dir: str):
        self.writer = SummaryWriter(f"{log_dir}/tb")

        self._models_dir = f"{log_dir}/models"
        os.makedirs(self._models_dir)

    def log_scalar(self, tag: str, val: float, step: int):
        self.writer.add_scalar(tag, val, step)

    def save_model(self, model, epoch: int):
        save_path = f"{self._models_dir}/encoder_epoch_{epoch}.pt"
        model.save_encoder(save_path)
        logging.info(f"Model saved in {save_path}")
