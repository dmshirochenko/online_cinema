from random import shuffle
import logging
from http import HTTPStatus

import aiohttp
import json
from redis import Redis
from pydantic import TypeAdapter

from ..settings import app_settings as conf
from ..models.request_responce import MovieOut, UserViewCountIn, MovieIn


class DBGeneralRecs:
    def __init__(self, host: str, port: int):
        self.db = Redis(host, port, decode_responses=True)

    def get_movie_ids(self, user_id: str) -> list[str]:
        ids = []
        for i in range(self.db.llen(user_id)):
            ids.append(self.db.lindex(user_id, i))
        return ids


class DBSimilarRecs:
    def __init__(self, host: str, port: int):
        self.db = Redis(host, port, decode_responses=True)

    # TODO: Decide on the same format of storing list between redis dbs
    def get_movie_ids(self, movie_id: str) -> list[str] | None:
        json_data = self.db.get(movie_id)
        if json_data is None:
            return None
        return json.loads(json_data)


class RecSysManager:
    redis: Redis

    def __init__(self):
        self.redis = Redis(host=conf.redis_host, port=conf.redis_port)
        self.db_general = DBGeneralRecs(conf.db_general_host, port=conf.db_general_port)
        self.db_similar = DBSimilarRecs(conf.db_similar_host, port=conf.db_similar_port)

    def _gen_movie(self) -> MovieOut:
        return MovieOut(
            uuid="123456",
            title="test movie",
            genres=["str1", "str2"],
            description="str",
            rating=5.3,
            director="str",
        )

    async def _get_count_user_views(self, user_id: str) -> int:
        """Get count of users views content."""
        view_count = self.redis.get(user_id)
        if view_count:
            return view_count.decode()
        async with aiohttp.ClientSession() as session:
            params = {"user_id": user_id}
            async with session.get(
                f"http://{conf.ugc_api_url}:8000/{conf.usc_api_user_viewed_count}/",
                params=params,
                timeout=conf.request_timeout_secs,
            ) as response:
                if response.status != HTTPStatus.OK:
                    raise RuntimeError("RecSys API couldn't processes request")

                text = await response.text()
                json_data = json.loads(text)
                view_count = TypeAdapter(UserViewCountIn).validate_json(json_data)
                await self.redis.set(user_id, view_count)
                return view_count

    def _convert_movie(self, movie_in: MovieIn) -> MovieOut:
        """Convert movie data to another format"""
        movie = self._gen_movie()
        movie.uuid = movie_in.id
        movie.title = movie_in.title
        movie.rating = movie_in.imdb_rating
        return movie

    async def _gen_cold_recommendations(self, user_id: str) -> list[MovieOut]:
        """Generate cold recommendation"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{conf.content_api_url}:8000/{conf.content_api_popular_movies}/",
            ) as response:
                text = await response.text()
                json_data = json.loads(text)
                films = []
                for film in json_data:
                    film_in = TypeAdapter(MovieIn).validate_json(film)
                    film_out = self._convert_movie(film_in)
                    films.append(film_out)
                return films

    async def _get_movie_info(self, movie_id: str) -> MovieOut:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{conf.content_api_url}:8000/api/v1/films/{movie_id}") as response:
                json_data = await response.json()

                return MovieOut(
                    uuid=json_data["id"],
                    title=json_data["title"],
                    genres=[g["name"] for g in json_data["genres"]],
                    description="",
                    rating=json_data["imdb_rating"],
                    director=",".join([d["full_name"] for d in json_data["directors"]]),
                )

    async def _gen_general_recommendations(self, user_id: str) -> list[MovieOut]:
        """Generate ML recommendation."""
        movie_ids = self.db_general.get_movie_ids(user_id)

        shuffle(movie_ids)
        if len(movie_ids) > conf.recsys_n_recs:
            movie_ids = movie_ids[: conf.recsys_n_recs]

        movies = []
        for _id in movie_ids:
            movie = await self._get_movie_info(_id)
            movies.append(movie)
        return movies

    async def general_recommendations(self, user_id: str) -> list[MovieOut]:
        # user_count_views = await self._get_count_user_views(user_id)
        # if user_count_views < conf.min_stored_actions:
        #     return await self._gen_cold_recommendations(user_id)

        movie_recs = await self._gen_general_recommendations(user_id)
        if len(movie_recs) == 0:
            logging.warning(f"Failed to get recommendations for user {user_id}.")
            return await self._gen_cold_recommendations(user_id)

        return movie_recs

    async def similar_movie_recommendations(self, content_id: str) -> list[MovieOut]:
        movie_ids = self.db_similar.get_movie_ids(content_id)
        if movie_ids is None:
            raise RuntimeError("Can't access similar recomendations data.")
        shuffle(movie_ids)
        # TODO: move logic of limiting the number of returned of ids from worker here

        movies = []
        for _id in movie_ids:
            movie = await self._get_movie_info(_id)
            movies.append(movie)
        return movies
