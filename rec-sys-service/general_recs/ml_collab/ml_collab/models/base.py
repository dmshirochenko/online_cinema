from abc import ABC, abstractmethod
from typing import Iterable

import pandas as pd

from ml_collab.data_loaders.base import DataLoader


class RecSysModel(ABC):
    @abstractmethod
    def train_test(self, df_train: Iterable, df_test: Iterable):
        pass

    @abstractmethod
    def train(self, df: Iterable):
        pass

    @abstractmethod
    def save_model(path: str):
        pass

    @abstractmethod
    def load_model(path: str):
        pass

    @abstractmethod
    def make_recommendations(self, data_loader: DataLoader, n_recommendations: int) -> pd.DataFrame:
        pass
