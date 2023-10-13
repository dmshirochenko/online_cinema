import logging
from http import HTTPStatus

from fastapi import APIRouter

from models import ReviewLike, Review
from core import ReviewManager
from settings import app_settings as conf


logger = logging.getLogger(__name__)
logger.setLevel(conf.logging_level)


router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={"404": {"description": "Not Found"}},
)


review_manager = ReviewManager(
    mongo_url=conf.mongo_url,
    db_name=conf.db_name,
    collection_name=conf.db_review_collection,
)


@router.post("/api/v1/add_review_like")
async def add_review_like(review_like: ReviewLike):
    """Do add  review_like route.

    Args:
        review_like (ReviewLike): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("add review like: {0}".format(dict(review_like)))

    await review_manager.add_like(
        review_id=review_like.review_id,
        user_id=review_like.user_id,
    )

    return {}, HTTPStatus.OK


@router.post("/api/v1/add_review_dislike")
async def add_review_dislike(review_dislike: ReviewLike):
    """Do add review_dislike route.

    Args:
        review_dislike (ReviewLike): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("add review like: {0}".format(dict(review_dislike)))

    await review_manager.add_dislike(
        review_id=review_dislike.review_id,
        user_id=review_dislike.user_id,
    )

    return {}, HTTPStatus.OK


@router.post("/api/v1/add_review")
async def add_review(review: Review):
    """Do remove like route.

    Args:
        review (Review): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("add review: {0}".format(dict(review)))

    await review_manager.add_review(
        movie_id=review.movie_id,
        user_id=review.user_id,
        review_text=review.text,
    )

    return {}, HTTPStatus.OK
