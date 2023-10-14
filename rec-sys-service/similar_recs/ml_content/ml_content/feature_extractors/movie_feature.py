import logging
import pickle

import numpy as np
import numpy.typing as npt
from sklearn.preprocessing import MultiLabelBinarizer

from ml_content.feature_extractors.base import AbstractFeatureExtractor
from ml_content.feature_extractors.text_feature import TextFeatureExtractor


class MovieFeatureExtractor(AbstractFeatureExtractor):
    """Return vector of features given the movie info."""

    def __init__(self, text_feature_extractor: TextFeatureExtractor, load_path: str | None = None):
        """
        Args:
            text_feature_extractor: Feature exractor to get an embedding fromg given text.
            load_path: Path to the object on disk to load from.
        """
        self._text_feature_extractor = text_feature_extractor

        self._mlb_genres = None
        if load_path:
            with open(load_path, "rb") as f:
                self._mlb_genres = pickle.load(f)["_mlb_genres"]

    def transform(self, film_info: dict) -> npt.ArrayLike:
        title_features = self._text_feature_extractor.transform(film_info["title"])

        desc_features = self._text_feature_extractor.transform(film_info["description"])

        genres = [x["name"] for x in film_info["genres"]]
        genres_binary = self._mlb_genres.transform([genres]).flatten()

        rating = film_info["imdb_rating"]
        rating = np.array([rating])

        actors_list = [x["full_name"] for x in film_info["actors"]]
        writers_list = [x["full_name"] for x in film_info["writers"]]
        directors_list = [x["full_name"] for x in film_info["directors"]]
        crew_desc = (
            f"Director: {' '.join(directors_list)} Writers: {' '.join(writers_list)} Actors: {' '.join(actors_list)}"
        )

        crew_features = self._text_feature_extractor.transform(crew_desc)

        movie_features = np.concatenate([title_features, desc_features, crew_features, genres_binary, rating])

        return movie_features

    def set_genres_mlb(self, genres: list[str]) -> None:
        self._mlb_genres = MultiLabelBinarizer()
        self._mlb_genres.fit(np.array(genres).reshape(-1, 1))

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump({"_mlb_genres": self._mlb_genres}, f)
        logging.info(f"MovieFeatureExtractor saved in {path}")

    @property
    def feature_dim(self) -> int:
        assert self._mlb_genres is not None, "Please call `set_genres_mlb` before calling `feature_dim`"
        return len(self._mlb_genres.classes_) + 768 * 3 + 1
