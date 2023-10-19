# File: tests/test_send_event.py
import sys
import os

import httpx
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import base_url


def test_add_and_check_watched_movie():
    # Setup: add a watched movie
    user_id = str(uuid4())
    movie_id = str(uuid4())
    response = httpx.post(
        f"{base_url}/watched/api/v1/add_watched_movie", json={"user_id": user_id, "movie_id": movie_id}
    )
    assert response.status_code == 200

    # Test: check that the movie is marked as watched
    response = httpx.get(
        f"{base_url}/watched/api/v1/is_movie_watched", params={"user_id": user_id, "movie_id": movie_id}
    )
    assert response.status_code == 200
    assert response.json()["watched"] is True

    # Test: check the count of watched movies
    response = httpx.get(f"{base_url}/watched/api/v1/get_watched_movies_count", params={"user_id": user_id})
    assert response.status_code == 200
    assert response.json() == 1


def test_get_most_watched_movies():
    response = httpx.get(f"{base_url}/watched/api/v1/get_most_watched_movies", params={"limit": 10})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
