import uuid
import logging
from http import HTTPStatus

from fastapi import APIRouter

from models import Like
from core import RatingManager
from settings import app_settings as conf


logger = logging.getLogger(__name__)
logger.setLevel(conf.logging_level)


router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
    responses={"404": {"description": "Not Found"}},
)

rating_manager = RatingManager(
    mongo_url=conf.mongo_url,
    db_name=conf.db_name,
    collection_name=conf.db_rating_collection,
)


@router.post("/api/v1/add_like")
async def add_like(like: Like):
    """Do add like route.

    Args:
        like (Like): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("add like: {0}".format(dict(like)))

    await rating_manager.add_like(movie_id=like.movie_id, user_id=like.user_id)

    return {}, HTTPStatus.OK


@router.delete("/api/v1/remove_like")
async def remove_like(like: Like):
    """Do remove like route.

    Args:
        like (Like): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("remove like: {0}".format(dict(like)))

    await rating_manager.add_dislike(movie_id=like.movie_id, user_id=like.user_id)

    return {}, HTTPStatus.OK


@router.get("/api/v1/get_num_movie_likes")
async def get_num_movie_likes(movie_id: uuid.UUID):
    """Get number of likes for a given movie.

    Args:
        movie_id: if of a movie.

    Returns:
        message: message with number of likes.
        http_status: status of response.
    """
    logger.debug("get num likes")
    num_likes = await rating_manager.get_num_likes(movie_id=movie_id)

    return {"num_likes": num_likes}, HTTPStatus.OK


@router.get("/api/v1/get_liked_movies")
async def get_liked_movies(user_id: uuid.UUID):
    """Get all movies liked by a specific user.

    Args:
        user_id: ID of a user.

    Returns:
        message: message with list of liked movie IDs.
        http_status: status of response.
    """
    logger.debug("get liked movies")
    liked_movies = await rating_manager.get_liked_movies(user_id=user_id)

    return {"liked_movies": liked_movies}, HTTPStatus.OK
