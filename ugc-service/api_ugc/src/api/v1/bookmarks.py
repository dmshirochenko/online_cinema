import logging
from http import HTTPStatus

from fastapi import APIRouter

from models import Bookmark
from core import BookmarkManager
from settings import app_settings as conf


logger = logging.getLogger(__name__)
logger.setLevel(conf.logging_level)


router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
    responses={"404": {"description": "Not Found"}},
)

bookmark_manager = BookmarkManager(
    mongo_url=conf.mongo_url,
    db_name=conf.db_name,
    collection_name=conf.db_bookmark_collection,
)


@router.post("/api/v1/save_bookmark")
async def save_bookmark(bookmark: Bookmark):
    """Do save bookmark route.

    Args:
        bookmark (Bookmark): request data for send to DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("save bookmark: {0}".format(dict(bookmark)))

    await bookmark_manager.add_bookmark(user_id=bookmark.user_id, movie_id=bookmark.movie_id)

    return {}, HTTPStatus.OK


@router.delete("/api/v1/delete_bookmark")
async def delete_bookmark(bookmark: Bookmark):
    """Do remove bookmark route.

    Args:
        bookmark (Bookmark): request data for remove from DB

    Returns:
        message: empty message
        http_status: status of response
    """
    logger.debug("delete bookmark: {0}".format(dict(bookmark)))

    await bookmark_manager.remove_bookmark(user_id=bookmark.user_id, movie_id=bookmark.movie_id)

    return {}, HTTPStatus.OK
