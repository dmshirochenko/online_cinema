import numpy.typing as npt
from transformers import pipeline

from ml_content.feature_extractors.base import AbstractFeatureExtractor


class TextFeatureExtractor(AbstractFeatureExtractor):
    """Basic feature extractoer based on HuggingFace models."""

    def __init__(self, model_name: str):
        self._feature_extractor = pipeline("feature-extraction", model=model_name)

    def transform(self, text: str) -> npt.ArrayLike:
        emb = self._feature_extractor(text, return_tensors="pt")[0].numpy().mean(axis=0)
        return emb

    @property
    def save(path: str) -> None:
        pass

    @property
    def feature_dim(self) -> int:
        return 768
