"""Data models for api events."""

import uuid

from pydantic import BaseModel


class BasicAction(BaseModel):
    """Structure of basic all actions."""

    user_id: uuid.UUID


class Bookmark(BasicAction):
    """Structure of bookmark."""

    movie_id: uuid.UUID


class Like(BasicAction):
    """Structure of like."""

    movie_id: uuid.UUID


class ReviewLike(BasicAction):
    """Structure of review dislike."""

    review_id: str


class Review(BasicAction):
    """Structure of review."""

    movie_id: uuid.UUID
    text: str
    rating: int


class WatchedMovie(BasicAction):
    """Structure of watched movie."""

    movie_id: uuid.UUID
