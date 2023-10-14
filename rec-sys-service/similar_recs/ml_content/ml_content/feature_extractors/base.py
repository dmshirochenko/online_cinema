from abc import ABC, abstractmethod

import numpy.typing as npt


class AbstractFeatureExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def transform(self, data: dict) -> npt.ArrayLike:
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @property
    def feature_dim(self) -> int:
        pass
