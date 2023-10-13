import logging
from http import HTTPStatus

from fastapi import APIRouter
from uuid import UUID
from bson.binary import Binary

from models import WatchedMovie
from core import WatchedMoviesManager
from settings import app_settings as conf
from typing import Any, Dict, List, Union


logger = logging.getLogger(__name__)
logger.setLevel(conf.logging_level)

router = APIRouter(
    prefix="/watched",
    tags=["watched"],
    responses={"404": {"description": "Not Found"}},
)

watched_movies_manager = WatchedMoviesManager(
    mongo_url=conf.mongo_url,
    db_name=conf.db_name,
    collection_name=conf.db_watched_movies_collection,
)


@router.post("/api/v1/add_watched_movie")
async def add_watched_movie(watched_movie: WatchedMovie):
    logger.debug("Add watched movie: {0}".format(dict(watched_movie)))

    await watched_movies_manager.add_watched_movie(user_id=watched_movie.user_id, movie_id=watched_movie.movie_id)

    return {}, HTTPStatus.OK


@router.get("/api/v1/is_movie_watched")
async def is_movie_watched(user_id: UUID, movie_id: UUID) -> Dict[str, bool]:
    logger.debug(f"Check if movie {movie_id} has been watched by user {user_id}")
    watched = await watched_movies_manager.is_movie_watched(user_id=user_id, movie_id=movie_id)

    return {"watched": watched}


@router.get("/api/v1/get_watched_movies_count", response_model=int)
async def get_watched_movies_count(user_id: UUID):
    logger.debug("Get watched movies count for user: {0}".format(user_id))

    count = await watched_movies_manager.get_watched_movies_count(user_id=user_id)

    return count


@router.get("/api/v1/get_most_watched_movies", response_model=List[Dict[str, Union[Any, int]]])
async def get_most_watched_movies(num_movies: int = 100):
    logger.debug("Get most watched movies")

    most_watched_movies = await watched_movies_manager.get_most_watched_movies(limit=num_movies)

    return most_watched_movies
