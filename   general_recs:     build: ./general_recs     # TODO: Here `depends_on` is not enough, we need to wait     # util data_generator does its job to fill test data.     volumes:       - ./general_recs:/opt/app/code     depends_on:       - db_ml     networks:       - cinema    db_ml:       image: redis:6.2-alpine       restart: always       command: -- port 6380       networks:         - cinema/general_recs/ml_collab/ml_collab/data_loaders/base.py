from abc import ABC, abstractmethod
from typing import Iterable


class DataLoader(ABC):
    @abstractmethod
    def load_train_test(self, train_ratio: float) -> list[Iterable]:
        pass

    @abstractmethod
    def load_data(self) -> Iterable:
        pass

    @property
    def item_column(self):
        pass

    @property
    def user_column(self):
        pass

    @property
    def rating_column(self):
        pass
