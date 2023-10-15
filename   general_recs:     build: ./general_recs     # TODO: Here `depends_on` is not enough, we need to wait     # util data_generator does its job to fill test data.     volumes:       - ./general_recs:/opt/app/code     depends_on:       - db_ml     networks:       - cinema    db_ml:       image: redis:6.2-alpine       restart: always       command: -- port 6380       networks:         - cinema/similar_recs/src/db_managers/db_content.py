from typing import Generator
import requests

from settings import DBContentSettings


class Manager:
    def __init__(self, conf: DBContentSettings):
        self.conf = conf

    def get_num_movies(self):
        url = f"{self.conf.host}/api/v1/films/all_films?page[number]=1&page[size]=1"
        return requests.get(url).json()["found_number"]

    def iterate_movie_info(self) -> Generator:
        for _id in self._iterate_movie_id():
            yield self._get_movie_info(_id)

    def _get_movie_info(self, movie_id: str) -> dict:
        url = f"{self.conf.host}/api/v1/films/{movie_id}"
        return requests.get(url).json()

    def _iterate_movie_id(self) -> Generator:
        # TODO: Remove hardcoded max number of movies
        url = f"{self.conf.host}/api/v1/films/all_films?page[number]=1&page[size]=999"
        for movie_info in requests.get(url).json()["result"]:
            yield movie_info["id"]
