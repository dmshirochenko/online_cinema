import logging
import os
import pickle
from abc import ABC, abstractmethod

import numpy as np
import requests
from tqdm import tqdm

from ml_content.feature_extractors.base import AbstractFeatureExtractor


class DataLoader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_batch(self, batch_size: int):
        pass


class ContentDBDataLoader(DataLoader):
    """Loads all the database content into the memory in via content service api."""

    def __init__(
        self,
        api_url: str,
        train_ratio: float,
        val_ratio: float,
        feature_extractor: AbstractFeatureExtractor,
        cache_on_disk: bool = True,
    ):
        self._api_url = api_url
        self._feature_extractor = feature_extractor
        self._path_on_disk = "/tmp/dataset.pickle"

        # Need to collect all existing genres to get one-hot multilabel encoder
        self._prepare_genres_multilabel()

        self._data = None
        self._film_titles = []
        if os.path.exists(self._path_on_disk):
            with open(self._path_on_disk, "rb") as f:
                data_loaded = pickle.load(f)
                self._film_titles = data_loaded["titles"]
                self._data = data_loaded["features"]
                logging.info("Dataset loaded from disk.")
        else:
            self._load_db_data()

            if cache_on_disk and not os.path.exists(self._path_on_disk):
                logging.info(f"Saving dataset on disk: {self._path_on_disk}")
                with open(self._path_on_disk, "wb") as f:
                    pickle.dump({"titles": self._film_titles, "features": self._data}, f)
                    logging.info("Dataset saved.")

        n = self._data.shape[0]
        (
            self._train_inds,
            self._val_inds,
            self._test_inds,
        ) = self._get_train_val_test_inds(n, train_ratio, val_ratio)
        logging.info(f"Dataset split (rel): TRAIN {len(self._train_inds) / n:5.2f} "
                     f"VAL {len(self._val_inds) / n:5.2f} TEST {len(self._test_inds) / n:5.2f}")

        logging.info(f"Dataset split (abs): TRAIN {len(self._train_inds):5d} "
                     f"VAL {len(self._val_inds):5d} TEST {len(self._test_inds):5d}")

    def _get_train_val_test_inds(self, n: int, train_ratio: float, val_ratio: float):
        inds = np.random.permutation(n)
        test_inds = inds[: int(n * (1 - train_ratio))]
        n_train = int(n * train_ratio)
        val_inds = inds[len(test_inds): len(test_inds) + int(n_train * val_ratio)]
        train_inds = inds[len(test_inds) + len(val_inds):]
        return train_inds, val_inds, test_inds

    def _get_dataset_size(self) -> int:
        url = f"{self._api_url}/films/all_films?page[number]=1&page[size]=20"
        response = requests.get(url).json()
        return response["found_number"]

    def _load_db_data(self):
        n = self._get_dataset_size()
        url = f"{self._api_url}/films/all_films?page[number]=1&page[size]={n}"
        response = requests.get(url)
        films_data = response.json()["result"]

        self._data = np.zeros((n, self._feature_extractor.feature_dim))
        for i, film_desc in enumerate(tqdm(films_data)):
            film_info = self._get_film_info(film_desc["id"])
            features = self._feature_extractor.transform(film_info)
            self._data[i] = features
            self._film_titles.append(film_desc["title"])

        gb = (self._data.size * self._data.itemsize) / 1024 / 1024 / 1024
        logging.info(f"Dataset is loaded into memory. Total size: {gb:.2f} GB")

    def _get_film_info(self, _id: str):
        url = f"{self._api_url}/films/{_id}"
        return requests.get(url).json()

    def _prepare_genres_multilabel(self):
        # genres_data = requests.get(f"{self._api_url}/genres/").json()
        # genres = list(sorted([x["name"] for x in genres_data]))
        # TODO: It seems that the genres table has incomplete list of genres, so here we need to find all
        # unuqie genres exist in the films. This step would be hugely optimised if we store all existing
        # genres in the db table.

        n = self._get_dataset_size()
        url = f"{self._api_url}/films/all_films?page[number]=1&page[size]={n}"
        response = requests.get(url)
        films_data = response.json()["result"]

        genres = set()
        for film_desc in tqdm(films_data):
            film_info = self._get_film_info(film_desc["id"])
            for g in film_info["genres"]:
                genres.add(g["name"])
        genres = list(sorted(genres))
        self._feature_extractor.set_genres_mlb(genres)

        logging.info(f"Found {len(genres)} unique genres.")

    def get_batch(self, batch_size: int):
        for i in range(0, len(self._train_inds), batch_size):
            yield self._data[self._train_inds[i: i + batch_size], :]

        # Random shuffle training data after the epoch
        self._train_inds = np.random.permutation(self._train_inds)

    def get_val_data(self):
        return self._data[self._val_inds]

    def get_test_data(self):
        return self._data[self._test_inds]

    def get_samples_raw_features(self):
        print("titles and data shape: ", len(self._film_titles), self._data.shape)
        for i in range(len(self._film_titles)):  # self._data.shape[0]):
            yield self._film_titles[i], self._data[i]

    def get_db_size(self) -> int:
        if self._data is not None:
            return self._data.shape[0]
